"""Managed dictionary storage, catalog, operations, and UI contracts."""

from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from PyQt6.QtCore import QObject, QSettings, QUrl, pyqtSignal
from PyQt6.QtNetwork import QNetworkReply, QNetworkRequest

from qt_test_case import QtTestCase
from zapzap.core.config.dictionary_store import (
    DictionaryStore,
    DictionaryStorePreparation,
)
from zapzap.core.config.path_manager import PathManager
from zapzap.core.config.settings.spellcheck import SpellcheckSettings
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.environment.setup_manager import SetupManager
from zapzap.core.environment.environment_manager import EnvironmentManager, Packaging
from zapzap.features.dictionaries.dictionaries_manager import (
    DictionariesManager,
    DictionaryError,
    DictionaryOperationResult,
    DictionaryState,
)
from zapzap.features.dictionaries.dictionary_catalog import (
    DictionaryCatalogCache,
    DictionaryCatalogEntry,
    DictionaryCatalogSnapshot,
    MAX_DICTIONARIES,
    MAX_DICTIONARY_BYTES,
    parse_github_tree,
    parse_manifest,
)
from zapzap.features.dictionaries.dictionary_service import DictionaryService
from zapzap.features.dictionaries.dictionary_manager import open_dictionary_manager
from zapzap.features.dictionaries.system_dictionary_provisioner import (
    SystemDictionaryProvisioner,
)
from zapzap.ui.components import DictionaryManagerDialog


def make_manifest(filename="pt_BR.bdic", payload=b"compiled dictionary"):
    revision = "a" * 40
    return json.dumps(
        {
            "schema_version": 1,
            "catalog_revision": "qt-6.11-test",
            "dictionaries": [
                {
                    "code": filename.removesuffix(".bdic"),
                    "filename": filename,
                    "size": len(payload),
                    "sha256": sha256(payload).hexdigest(),
                    "qt_version": "6.11",
                    "source": "test",
                    "source_revision": revision,
                }
            ],
        }
    ).encode()


def write_complete_local_manifest(directory: Path) -> None:
    records = [
        {
            "filename": path.name,
            "size": path.stat().st_size,
        }
        for path in sorted(directory.glob("*.bdic"))
    ]
    (directory / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "catalog_revision": "test",
                "repository": DictionaryStore.CATALOG_REPOSITORY,
                "dictionaries": records,
            }
        ),
        encoding="utf-8",
    )


class FakeReply(QObject):
    readyRead = pyqtSignal()
    downloadProgress = pyqtSignal(int, int)
    finished = pyqtSignal()

    def __init__(self, url: str, *, status=200, error=None, etag=b""):
        super().__init__()
        self._url = QUrl(url)
        self._status = status
        self._error = error or QNetworkReply.NetworkError.NoError
        self._etag = etag
        self._buffer = bytearray()
        self._finished = False

    def attribute(self, attribute):
        if attribute == QNetworkRequest.Attribute.HttpStatusCodeAttribute:
            return self._status
        return None

    def rawHeader(self, name):
        return self._etag if bytes(name).lower() == b"etag" else b""

    def url(self):
        return self._url

    def error(self):
        return self._error

    def bytesAvailable(self):
        return len(self._buffer)

    def read(self, maximum):
        chunk = bytes(self._buffer[:maximum])
        del self._buffer[:maximum]
        return chunk

    def feed(self, payload=b"", *, total=None, finish=False):
        if self._finished:
            return
        self._buffer.extend(payload)
        if payload:
            self.readyRead.emit()
            self.downloadProgress.emit(len(payload), total or len(payload))
        if finish:
            self._finished = True
            self.finished.emit()

    def abort(self):
        if self._finished:
            return
        self._error = QNetworkReply.NetworkError.OperationCanceledError
        self._finished = True
        self.finished.emit()


class FakeNetwork(QObject):
    def __init__(self, replies):
        super().__init__()
        self.replies = list(replies)
        self.requests = []

    def get(self, request):
        self.requests.append(request)
        return self.replies.pop(0)


class FakeProvisionService(QObject):
    catalog_loaded = pyqtSignal(object)
    catalog_failed = pyqtSignal(str, bool)
    download_finished = pyqtSignal(str, object)

    def __init__(self):
        super().__init__()
        self.fetch_count = 0
        self.installed = []
        self.closed = False

    def fetch_catalog(self):
        self.fetch_count += 1

    def install(self, entry):
        self.installed.append(entry)

    def close(self):
        self.closed = True


class ManagedDictionaryStoreTests(QtTestCase):

    def setUp(self):
        super().setUp()
        self.temporary = tempfile.TemporaryDirectory(prefix="dictionary-store-")
        self.root = Path(self.temporary.name)
        self.managed = self.root / "managed"
        DictionaryStore.set_path_override_for_tests(self.managed)
        self.original_settings = SettingsManager._settings
        SettingsManager._settings = QSettings(
            str(self.root / "settings.ini"),
            QSettings.Format.IniFormat,
        )

    def tearDown(self):
        SettingsManager._settings = self.original_settings
        DictionaryStore.set_path_override_for_tests(None)
        self.temporary.cleanup()
        super().tearDown()

    def test_migration_is_atomic_idempotent_and_preserves_the_source(self):
        legacy = self.root / "legacy"
        legacy.mkdir()
        source = legacy / "pt_BR.bdic"
        source.write_bytes(b"dictionary")
        (legacy / "notes.txt").write_text("ignored", encoding="utf-8")

        first = DictionaryStore.prepare([legacy])
        second = DictionaryStore.prepare([legacy])

        self.assertEqual(first.migrated, ("pt_BR.bdic",))
        self.assertEqual(second.migrated, ())
        self.assertEqual((self.managed / "pt_BR.bdic").read_bytes(), b"dictionary")
        self.assertEqual(source.read_bytes(), b"dictionary")
        self.assertFalse((self.managed / "notes.txt").exists())
        self.assertTrue((self.managed / ".zapzap/migration-v1.json").is_file())

    def test_migration_rejects_symlinks_and_does_not_copy_outside_content(self):
        legacy = self.root / "legacy"
        legacy.mkdir()
        outside = self.root / "outside.bdic"
        outside.write_bytes(b"outside")
        link = legacy / "linked.bdic"
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest("symlinks are unavailable")

        result = DictionaryStore.prepare([legacy])

        self.assertEqual(result.migrated, ())
        self.assertFalse((self.managed / "linked.bdic").exists())

    def test_partial_migration_is_retried_and_never_overwrites_a_conflict(self):
        legacy = self.root / "legacy"
        legacy.mkdir()
        (legacy / "ok.bdic").write_bytes(b"ok")
        (legacy / "conflict.bdic").write_bytes(b"incoming")
        self.managed.mkdir()
        (self.managed / "conflict.bdic").write_bytes(b"managed")

        first = DictionaryStore.prepare([legacy])
        second = DictionaryStore.prepare([legacy])

        self.assertEqual(first.migrated, ("ok.bdic",))
        self.assertTrue(first.failures)
        self.assertTrue(second.failures)
        self.assertFalse((self.managed / ".zapzap/migration-v1.json").exists())
        self.assertEqual((self.managed / "conflict.bdic").read_bytes(), b"managed")
        self.assertEqual((legacy / "conflict.bdic").read_bytes(), b"incoming")

    def test_failed_store_creation_uses_only_an_existing_legacy_directory(self):
        legacy = self.root / "legacy"
        legacy.mkdir()
        with patch.object(DictionaryStore, "path", side_effect=OSError("denied")):
            result = DictionaryStore.prepare([self.root / "missing", legacy])

        self.assertEqual(result.path, str(legacy))
        self.assertTrue(result.used_fallback)
        self.assertIn("denied", result.failures[0])

    def test_import_conflict_preserves_the_installed_dictionary(self):
        self.managed.mkdir()
        (self.managed / "pt_BR.bdic").write_bytes(b"installed")
        incoming = self.root / "pt_BR.bdic"
        incoming.write_bytes(b"different")

        result = DictionariesManager.import_file(incoming)

        self.assertFalse(result.success)
        self.assertEqual(result.error, DictionaryError.CONFLICT)
        self.assertEqual((self.managed / "pt_BR.bdic").read_bytes(), b"installed")

        replaced = DictionariesManager.import_file(incoming, replace=True)
        self.assertTrue(replaced.success)
        self.assertEqual((self.managed / "pt_BR.bdic").read_bytes(), b"different")

    def test_failed_replacement_metadata_restores_the_installed_dictionary(self):
        self.managed.mkdir()
        installed = self.managed / "pt_BR.bdic"
        installed.write_bytes(b"installed")
        incoming = self.root / "pt_BR.bdic"
        incoming.write_bytes(b"replacement")

        with patch.object(
            DictionariesManager,
            "record_install",
            side_effect=OSError("metadata denied"),
        ):
            result = DictionariesManager.import_file(incoming, replace=True)

        self.assertFalse(result.success)
        self.assertEqual(installed.read_bytes(), b"installed")
        self.assertEqual(list(self.managed.glob("*.backup")), [])

    def test_removing_the_last_active_dictionary_requires_explicit_disable(self):
        self.managed.mkdir()
        source = self.root / "pt_BR.bdic"
        source.write_bytes(b"dictionary")
        self.assertTrue(DictionariesManager.import_file(source).success)
        DictionariesManager.set_selected_languages(["pt_BR"])
        SpellcheckSettings().enabled = True

        protected = DictionariesManager.remove("pt_BR")
        removed = DictionariesManager.remove("pt_BR", disable_if_last=True)

        self.assertEqual(protected.error, DictionaryError.LAST_ACTIVE)
        self.assertTrue(removed.success)
        self.assertFalse(SpellcheckSettings().enabled)
        self.assertFalse((self.managed / "pt_BR.bdic").exists())

    def test_removal_is_idempotent_and_permission_failure_preserves_selection(self):
        self.managed.mkdir()
        self.assertTrue(DictionariesManager.remove("missing").success)
        source = self.root / "pt_BR.bdic"
        source.write_bytes(b"dictionary")
        self.assertTrue(DictionariesManager.import_file(source).success)
        DictionariesManager.set_selected_languages(["pt_BR"])
        SpellcheckSettings().enabled = False

        with patch.object(Path, "unlink", side_effect=PermissionError("denied")):
            result = DictionariesManager.remove("pt_BR")

        self.assertEqual(result.error, DictionaryError.PERMISSION)
        self.assertEqual(DictionariesManager.get_selected_languages(), ["pt_BR"])
        self.assertTrue((self.managed / "pt_BR.bdic").exists())

    def test_local_and_remote_provenance_is_recorded_outside_the_bdic_set(self):
        self.managed.mkdir()
        source = self.root / "custom_name.bdic"
        source.write_bytes(b"dictionary")
        self.assertTrue(DictionariesManager.import_file(source).success)
        DictionariesManager.record_install(
            "remote_name",
            {
                "source": "catalog",
                "source_revision": "a" * 40,
                "sha256": "b" * 64,
                "size": 10,
            },
        )

        metadata = DictionariesManager._load_metadata()["dictionaries"]
        self.assertEqual(metadata["custom_name"]["source"], "local")
        self.assertIn("installed_at", metadata["custom_name"])
        self.assertEqual(metadata["remote_name"]["source"], "catalog")
        self.assertFalse((self.managed / "installed.json").exists())

    def test_setup_publishes_only_the_prepared_nonempty_path(self):
        result = DictionaryStorePreparation(str(self.managed))
        with (
            patch.object(DictionaryStore, "prepare", return_value=result),
            patch.object(PathManager, "get_default_path", return_value=""),
            patch("zapzap.core.environment.setup_manager.PathManager.get_paths", return_value={}),
            patch("zapzap.core.environment.setup_manager.preferred_render_node", return_value=None),
            patch("zapzap.core.environment.setup_manager.has_headless_secondary_gpu", return_value=False),
            patch.object(SettingsManager, "get", side_effect=lambda _key, default=None: default),
        ):
            SetupManager.apply()

        self.assertEqual(
            os.environ["QTWEBENGINE_DICTIONARIES_PATH"], str(self.managed)
        )

    def test_setup_removes_an_invalid_empty_dictionary_override(self):
        with (
            patch.dict(
                os.environ,
                {"QTWEBENGINE_DICTIONARIES_PATH": "/missing"},
                clear=True,
            ),
            patch.object(
                DictionaryStore,
                "prepare",
                return_value=DictionaryStorePreparation(None),
            ),
            patch.object(PathManager, "get_default_path", return_value=""),
            patch("zapzap.core.environment.setup_manager.PathManager.get_paths", return_value={}),
            patch("zapzap.core.environment.setup_manager.preferred_render_node", return_value=None),
            patch("zapzap.core.environment.setup_manager.has_headless_secondary_gpu", return_value=False),
            patch.object(SettingsManager, "get", side_effect=lambda _key, default=None: default),
        ):
            SetupManager.apply()
            self.assertNotIn("QTWEBENGINE_DICTIONARIES_PATH", os.environ)

    def test_package_default_catalog_is_used_without_copying_it(self):
        package_default = self.root / "package-default"
        package_default.mkdir()
        (package_default / "pt_BR.bdic").write_bytes(b"packaged dictionary")
        write_complete_local_manifest(package_default)
        with (
            patch.dict(
                os.environ,
                {
                    "APPIMAGE": str(self.root / "ZapZap.AppImage"),
                    "QTWEBENGINE_DICTIONARIES_PATH": str(self.root / "ignored"),
                },
                clear=True,
            ),
            patch.object(
                EnvironmentManager,
                "identify_packaging",
                return_value=Packaging.APPIMAGE,
            ),
            patch.object(
                PathManager,
                "get_default_path",
                return_value=str(package_default),
            ),
            patch.object(DictionaryStore, "prepare") as prepare,
            patch(
                "zapzap.core.environment.setup_manager.PathManager.get_paths"
            ) as legacy_paths,
            patch(
                "zapzap.core.environment.setup_manager.preferred_render_node",
                return_value=None,
            ),
            patch(
                "zapzap.core.environment.setup_manager.has_headless_secondary_gpu",
                return_value=False,
            ),
            patch.object(
                SettingsManager,
                "get",
                side_effect=lambda _key, default=None: default,
            ),
        ):
            SetupManager.apply()

            self.assertEqual(
                os.environ["QTWEBENGINE_DICTIONARIES_PATH"], str(package_default)
            )
            self.assertEqual(DictionariesManager.get_path(), str(package_default))
            self.assertFalse(DictionariesManager.is_management_available())
            self.assertEqual(DictionariesManager.list(), ["pt_BR"])
            with patch.object(
                DictionariesManager,
                "get_system_language",
                return_value="pt_BR",
            ):
                self.assertEqual(
                    DictionariesManager.get_selected_languages(),
                    ["pt_BR"],
                )
            self.assertEqual(
                DictionariesManager.import_file(package_default / "pt_BR.bdic").error,
                DictionaryError.MANAGED_EXTERNALLY,
            )
            self.assertEqual(
                DictionariesManager.remove("pt_BR").error,
                DictionaryError.MANAGED_EXTERNALLY,
            )
            prepare.assert_not_called()
            legacy_paths.assert_not_called()
            self.assertFalse(self.managed.exists())

    def test_partial_package_catalog_uses_managed_store_and_keeps_management(self):
        package_default = self.root / "partial-package-default"
        package_default.mkdir()
        for code in ("en_AU", "en_CA", "en_GB", "en_US", "en_ZA"):
            (package_default / f"{code}.bdic").write_bytes(code.encode())

        with (
            patch.dict(
                os.environ,
                {
                    "FLATPAK_ID": "com.rtosta.zapzap",
                    "QTWEBENGINE_DICTIONARIES_PATH": str(package_default),
                },
                clear=True,
            ),
            patch.object(
                EnvironmentManager,
                "identify_packaging",
                return_value=Packaging.FLATPAK,
            ),
            patch.object(
                PathManager,
                "get_default_path",
                return_value=str(package_default),
            ),
            patch.object(
                DictionaryStore,
                "prepare",
                return_value=DictionaryStorePreparation(str(self.managed)),
            ) as prepare,
            patch(
                "zapzap.core.environment.setup_manager.PathManager.get_paths",
                return_value={"path": str(package_default)},
            ),
            patch(
                "zapzap.core.environment.setup_manager.preferred_render_node",
                return_value=None,
            ),
            patch(
                "zapzap.core.environment.setup_manager.has_headless_secondary_gpu",
                return_value=False,
            ),
            patch.object(
                SettingsManager,
                "get",
                side_effect=lambda _key, default=None: default,
            ),
        ):
            SetupManager.apply()

            self.assertEqual(
                os.environ["QTWEBENGINE_DICTIONARIES_PATH"], str(self.managed)
            )
            self.assertTrue(DictionariesManager.is_management_available())

        prepare.assert_called_once_with(
            (str(package_default), str(package_default), str(package_default))
        )

    def test_complete_catalog_requires_manifest_to_match_files_and_sizes(self):
        catalog = self.root / "catalog"
        catalog.mkdir()
        dictionary = catalog / "pt_BR.bdic"
        dictionary.write_bytes(b"dictionary")

        self.assertFalse(DictionaryStore.is_complete_dictionary_catalog(catalog))
        write_complete_local_manifest(catalog)
        self.assertTrue(DictionaryStore.is_complete_dictionary_catalog(catalog))

        dictionary.write_bytes(b"changed size")
        self.assertFalse(DictionaryStore.is_complete_dictionary_catalog(catalog))

    def test_empty_package_default_falls_back_to_managed_store(self):
        with (
            patch.dict(
                os.environ,
                {
                    "APPIMAGE": str(self.root / "ZapZap.AppImage"),
                    "QTWEBENGINE_DICTIONARIES_PATH": str(self.root / "missing"),
                },
                clear=True,
            ),
            patch.object(
                EnvironmentManager,
                "identify_packaging",
                return_value=Packaging.APPIMAGE,
            ),
            patch.object(
                PathManager,
                "get_default_path",
                return_value=str(self.root / "empty-default"),
            ),
            patch.object(
                DictionaryStore,
                "prepare",
                return_value=DictionaryStorePreparation(str(self.managed)),
            ) as prepare,
            patch(
                "zapzap.core.environment.setup_manager.PathManager.get_paths",
                return_value={},
            ),
            patch(
                "zapzap.core.environment.setup_manager.preferred_render_node",
                return_value=None,
            ),
            patch(
                "zapzap.core.environment.setup_manager.has_headless_secondary_gpu",
                return_value=False,
            ),
            patch.object(
                SettingsManager,
                "get",
                side_effect=lambda _key, default=None: default,
            ),
        ):
            SetupManager.apply()

            self.assertEqual(
                os.environ["QTWEBENGINE_DICTIONARIES_PATH"], str(self.managed)
            )
            self.assertTrue(DictionariesManager.is_management_available())
            prepare.assert_called_once()

    def test_system_language_candidate_never_falls_back_to_another_language(self):
        with patch.object(
            DictionariesManager,
            "get_system_language",
            return_value="pt_PT",
        ):
            self.assertEqual(
                DictionariesManager.system_language_candidate(
                    ["en_US", "pt_BR", "es_ES"]
                ),
                "pt_BR",
            )
            self.assertIsNone(
                DictionariesManager.system_language_candidate(["en_US", "es_ES"])
            )

    def test_system_dictionary_provisioner_downloads_only_the_system_language(self):
        service = FakeProvisionService()
        provisioner = SystemDictionaryProvisioner(service=service)
        entries = (
            DictionaryCatalogEntry(
                code="en_US",
                filename="en_US.bdic",
                size=2,
                sha256=sha256(b"en").hexdigest(),
                source_revision="a" * 40,
                source="test",
            ),
            DictionaryCatalogEntry(
                code="pt_BR",
                filename="pt_BR.bdic",
                size=2,
                sha256=sha256(b"pt").hexdigest(),
                source_revision="a" * 40,
                source="test",
            ),
        )
        snapshot = DictionaryCatalogSnapshot(
            entries=entries,
            revision="test",
            fetched_at="now",
        )
        with (
            patch.object(
                DictionariesManager,
                "get_system_language",
                return_value="pt_BR",
            ),
            patch.object(
                DictionariesManager,
                "is_management_available",
                return_value=True,
            ),
        ):
            self.assertTrue(provisioner.start())
            service.catalog_loaded.emit(snapshot)

        self.assertEqual(service.fetch_count, 1)
        self.assertEqual([entry.code for entry in service.installed], ["pt_BR"])

    def test_successful_system_provision_is_one_time_and_keeps_other_languages_manual(self):
        service = FakeProvisionService()
        provisioner = SystemDictionaryProvisioner(service=service)
        entry = DictionaryCatalogEntry(
            code="pt_BR",
            filename="pt_BR.bdic",
            size=2,
            sha256=sha256(b"pt").hexdigest(),
            source_revision="a" * 40,
            source="test",
        )
        snapshot = DictionaryCatalogSnapshot(
            entries=(entry,),
            revision="test",
            fetched_at="now",
        )
        installed = []
        with (
            patch.object(
                DictionariesManager,
                "get_system_language",
                return_value="pt_BR",
            ),
            patch.object(
                DictionariesManager,
                "is_management_available",
                return_value=True,
            ),
            patch.object(DictionariesManager, "record_install") as record,
        ):
            provisioner.dictionary_installed.connect(installed.append)
            self.assertTrue(provisioner.start())
            service.catalog_loaded.emit(snapshot)
            (self.managed / "pt_BR.bdic").parent.mkdir(parents=True, exist_ok=True)
            (self.managed / "pt_BR.bdic").write_bytes(b"pt")
            service.download_finished.emit(
                "pt_BR",
                DictionaryOperationResult(True, "pt_BR"),
            )
            (self.managed / "pt_BR.bdic").unlink()
            second_service = FakeProvisionService()
            second = SystemDictionaryProvisioner(service=second_service)
            self.assertFalse(second.start())
            self.assertEqual(second_service.fetch_count, 0)

        record.assert_called_once()
        self.assertEqual(installed, ["pt_BR"])
        self.assertEqual(
            SettingsManager.get(
                SystemDictionaryProvisioner._PROVISIONED_LOCALE_KEY
            ),
            "pt_BR",
        )

    def test_package_catalog_skips_even_constructing_the_network_service(self):
        with (
            patch.object(
                DictionariesManager,
                "is_management_available",
                return_value=False,
            ),
            patch(
                "zapzap.features.dictionaries.system_dictionary_provisioner."
                "DictionaryService"
            ) as service,
        ):
            self.assertFalse(SystemDictionaryProvisioner().start())

        service.assert_not_called()

    def test_existing_system_dictionary_is_marked_without_network(self):
        self.managed.mkdir()
        (self.managed / "pt_BR.bdic").write_bytes(b"installed")
        with (
            patch.object(
                DictionariesManager,
                "get_system_language",
                return_value="pt_BR",
            ),
            patch.object(
                DictionariesManager,
                "is_management_available",
                return_value=True,
            ),
            patch(
                "zapzap.features.dictionaries.system_dictionary_provisioner."
                "DictionaryService"
            ) as service,
        ):
            self.assertFalse(SystemDictionaryProvisioner().start())

        service.assert_not_called()
        self.assertEqual(
            SettingsManager.get(
                SystemDictionaryProvisioner._PROVISIONED_LOCALE_KEY
            ),
            "pt_BR",
        )


class DictionaryCatalogTests(unittest.TestCase):

    def test_manifest_parsing_keeps_codes_and_pins_downloads_to_revision(self):
        snapshot = parse_manifest(make_manifest())
        entry = snapshot.entries[0]

        self.assertEqual(entry.code, "pt_BR")
        self.assertEqual(entry.sha256, sha256(b"compiled dictionary").hexdigest())
        self.assertEqual(
            entry.download_url,
            "https://raw.githubusercontent.com/rafatosta/"
            "qtwebengine_dictionaries/" + "a" * 40 + "/pt_BR.bdic",
        )

    def test_manifest_rejects_traversal_duplicate_and_bad_hash(self):
        for filename, digest in (
            ("../pt_BR.bdic", "0" * 64),
            ("pt_BR.bdic", "bad"),
        ):
            data = json.loads(make_manifest())
            data["dictionaries"][0]["filename"] = filename
            data["dictionaries"][0]["code"] = filename.removesuffix(".bdic")
            data["dictionaries"][0]["sha256"] = digest
            with self.subTest(filename=filename, digest=digest):
                with self.assertRaises(ValueError):
                    parse_manifest(json.dumps(data).encode())

    def test_manifest_enforces_entry_name_and_file_size_limits(self):
        too_many = json.loads(make_manifest())
        too_many["dictionaries"] *= MAX_DICTIONARIES + 1
        too_large = json.loads(make_manifest())
        too_large["dictionaries"][0]["size"] = MAX_DICTIONARY_BYTES + 1
        long_name = json.loads(make_manifest())
        filename = "a" * 161 + ".bdic"
        long_name["dictionaries"][0]["filename"] = filename
        long_name["dictionaries"][0]["code"] = filename.removesuffix(".bdic")

        for payload in (too_many, too_large, long_name):
            with self.assertRaises(ValueError):
                parse_manifest(json.dumps(payload).encode())

    def test_github_tree_fallback_accepts_only_safe_root_bdic_blobs(self):
        tree = json.dumps(
            {
                "truncated": False,
                "tree": [
                    {"path": "pt_BR.bdic", "type": "blob", "size": 20, "sha": "b" * 40},
                    {"path": "docs/nested.bdic", "type": "blob", "size": 20, "sha": "c" * 40},
                    {"path": "README.md", "type": "blob", "size": 20, "sha": "d" * 40},
                ],
            }
        ).encode()

        snapshot = parse_github_tree(tree, commit_revision="a" * 40)

        self.assertEqual([entry.code for entry in snapshot.entries], ["pt_BR"])
        self.assertEqual(snapshot.entries[0].git_sha, "b" * 40)

    def test_validated_catalog_cache_remains_available_offline(self):
        with tempfile.TemporaryDirectory(prefix="dictionary-cache-") as directory:
            cache = DictionaryCatalogCache(directory)
            snapshot = parse_manifest(make_manifest())
            cache.save(snapshot)

            loaded = cache.load()

        self.assertIsNotNone(loaded)
        self.assertTrue(loaded.stale)
        self.assertEqual(loaded.entries[0].code, "pt_BR")

    def test_network_allowlist_rejects_wrong_hosts_and_unpinned_files(self):
        from PyQt6.QtCore import QUrl

        self.assertTrue(
            DictionaryService._valid_final_url(
                QUrl(
                    "https://raw.githubusercontent.com/rafatosta/"
                    "qtwebengine_dictionaries/main/manifest.json"
                )
            )
        )
        self.assertFalse(
            DictionaryService._valid_final_url(
                QUrl("https://example.com/manifest.json")
            )
        )
        self.assertFalse(
            DictionaryService._valid_final_url(
                QUrl(
                    "https://raw.githubusercontent.com/rafatosta/"
                    "qtwebengine_dictionaries/main/pt_BR.bdic"
                ),
                expected_filename="pt_BR.bdic",
            )
        )


class DictionaryDownloadTests(QtTestCase):

    def setUp(self):
        super().setUp()
        self.temporary = tempfile.TemporaryDirectory(prefix="dictionary-download-")
        self.root = Path(self.temporary.name)
        self.cache = DictionaryCatalogCache(self.root / "cache")

    def tearDown(self):
        self.temporary.cleanup()
        super().tearDown()

    @staticmethod
    def entry(code, payload):
        return DictionaryCatalogEntry(
            code=code,
            filename=f"{code}.bdic",
            size=len(payload),
            sha256=sha256(payload).hexdigest(),
            source_revision="a" * 40,
            source="test",
            qt_version="6.11",
        )

    def test_incremental_verified_download_is_committed_atomically(self):
        payload = b"compiled dictionary"
        entry = self.entry("pt_BR", payload)
        reply = FakeReply(entry.download_url)
        service = DictionaryService(
            network=FakeNetwork([reply]),
            cache=self.cache,
            destination=self.root / "installed",
        )
        results = []
        service.download_finished.connect(lambda _code, result: results.append(result))

        service.install(entry)
        reply.feed(payload[:7], total=len(payload))
        reply.feed(payload[7:], total=len(payload), finish=True)

        self.assertTrue(results[-1].success)
        self.assertEqual(
            (self.root / "installed/pt_BR.bdic").read_bytes(), payload
        )
        self.assertEqual(list((self.root / "installed").glob("*.part")), [])

    def test_hash_or_size_failure_and_cancel_leave_no_partial_dictionary(self):
        cases = (
            ("bad_hash", b"payloae", False, DictionaryError.HASH),
            ("too_large", b"payload-extra", False, DictionaryError.SIZE),
            ("cancelled", b"partial", True, DictionaryError.CANCELLED),
        )
        for code, received, cancel, expected in cases:
            with self.subTest(code=code):
                entry = self.entry(code, b"payload")
                reply = FakeReply(entry.download_url)
                service = DictionaryService(
                    network=FakeNetwork([reply]),
                    cache=self.cache,
                    destination=self.root / code,
                )
                results = []
                service.download_finished.connect(
                    lambda _code, result: results.append(result)
                )
                service.install(entry)
                if cancel:
                    reply.feed(received, total=entry.size)
                    service.cancel(code)
                else:
                    reply.feed(received, total=len(received), finish=True)

                self.assertEqual(results[-1].error, expected)
                self.assertFalse((self.root / code / entry.filename).exists())

    def test_existing_dictionary_is_preserved_and_concurrency_is_bounded(self):
        destination = self.root / "installed"
        destination.mkdir()
        (destination / "existing.bdic").write_bytes(b"installed")
        replies = [
            FakeReply(self.entry(code, b"payload").download_url)
            for code in ("one", "two")
        ]
        network = FakeNetwork(replies)
        service = DictionaryService(
            network=network,
            cache=self.cache,
            destination=destination,
        )
        results = []
        service.download_finished.connect(lambda _code, result: results.append(result))

        service.install(self.entry("existing", b"replacement"))
        service.install(self.entry("one", b"payload"))
        service.install(self.entry("one", b"payload"))
        service.install(self.entry("two", b"payload"))
        service.install(self.entry("three", b"payload"))

        self.assertEqual((destination / "existing.bdic").read_bytes(), b"installed")
        self.assertEqual(len(network.requests), 2)
        self.assertEqual([result.error for result in results], [
            DictionaryError.CONFLICT,
            DictionaryError.BUSY,
        ])
        service.close()

    def test_downloads_over_the_limit_are_queued_and_started_in_order(self):
        payload = b"payload"
        entries = [self.entry(code, payload) for code in ("one", "two", "three")]
        replies = [FakeReply(entry.download_url) for entry in entries]
        network = FakeNetwork(replies)
        service = DictionaryService(
            network=network,
            cache=self.cache,
            destination=self.root / "installed",
        )
        results = []
        service.download_finished.connect(lambda code, result: results.append((code, result)))

        for entry in entries:
            service.install(entry)
        self.assertEqual(len(network.requests), 2)

        replies[0].feed(payload, total=len(payload), finish=True)
        self.assertEqual(len(network.requests), 3)
        replies[1].feed(payload, total=len(payload), finish=True)
        replies[2].feed(payload, total=len(payload), finish=True)

        self.assertEqual([code for code, result in results if result.success], [
            "one", "two", "three"
        ])

    def test_304_reuses_the_validated_cached_catalog_and_sends_etag(self):
        snapshot = self.cache.with_etag(parse_manifest(make_manifest()), '"etag"')
        self.cache.save(snapshot)
        reply = FakeReply(
            "https://raw.githubusercontent.com/rafatosta/"
            "qtwebengine_dictionaries/main/manifest.json",
            status=304,
        )
        network = FakeNetwork([reply])
        service = DictionaryService(network=network, cache=self.cache)
        loaded = []
        service.catalog_loaded.connect(loaded.append)

        service.fetch_catalog()
        reply.feed(finish=True)

        self.assertEqual(bytes(network.requests[0].rawHeader(b"If-None-Match")), b'"etag"')
        self.assertEqual(loaded[0].entries[0].code, "pt_BR")

    def test_offline_uses_cache_and_without_cache_reports_recoverable_failure(self):
        service = DictionaryService(
            network=FakeNetwork([]),
            cache=self.cache,
            destination=self.root / "installed",
        )
        loaded = []
        failures = []
        service.catalog_loaded.connect(loaded.append)
        service.catalog_failed.connect(lambda detail, cache: failures.append((detail, cache)))

        service._catalog_failure("offline")
        self.assertEqual(loaded, [])
        self.assertEqual(failures[-1], ("offline", False))

        self.cache.save(parse_manifest(make_manifest()))
        service._catalog_failure("offline")
        self.assertEqual(loaded[-1].entries[0].code, "pt_BR")
        self.assertEqual(failures[-1], ("offline", True))

    def test_timeout_rate_limit_and_http_errors_are_distinguishable(self):
        cases = (
            (0, QNetworkReply.NetworkError.TimeoutError, DictionaryError.TIMEOUT),
            (403, QNetworkReply.NetworkError.NoError, DictionaryError.RATE_LIMIT),
            (500, QNetworkReply.NetworkError.NoError, DictionaryError.HTTP),
        )
        for index, (status, network_error, expected) in enumerate(cases):
            with self.subTest(expected=expected):
                entry = self.entry(f"error_{index}", b"payload")
                reply = FakeReply(
                    entry.download_url,
                    status=status,
                    error=network_error,
                )
                service = DictionaryService(
                    network=FakeNetwork([reply]),
                    cache=self.cache,
                    destination=self.root / f"error-{index}",
                )
                results = []
                service.download_finished.connect(
                    lambda _code, result: results.append(result)
                )

                service.install(entry)
                reply.feed(finish=True)

                self.assertEqual(results[-1].error, expected)


class DictionaryManagerUiTests(QtTestCase):

    def test_dialog_filters_labels_codes_and_installed_state(self):
        dialog = DictionaryManagerDialog()
        snapshot = DictionaryCatalogSnapshot(
            entries=parse_manifest(make_manifest()).entries,
            revision="test",
            fetched_at="2026-08-17T00:00:00+00:00",
        )
        states = [
            DictionaryState(
                "pt_BR", "Português (Brasil)", True, True, False, True
            ),
            DictionaryState(
                "es_ES", "Español (España)", False, False, False, True
            ),
        ]
        dialog.set_catalog(snapshot, states)

        dialog.search_edit.setText("portugues")
        visible = [
            not dialog.dictionary_tree.topLevelItem(index).isHidden()
            for index in range(dialog.dictionary_tree.topLevelItemCount())
        ]
        self.assertEqual(visible, [True, False])
        self.assertTrue(dialog.dictionary_tree.accessibleName())
        self.assertTrue(dialog.search_edit.accessibleDescription())

        dialog.search_edit.clear()
        dialog.filter_combo.setCurrentIndex(
            dialog.filter_combo.findData("available")
        )
        visible = [
            not dialog.dictionary_tree.topLevelItem(index).isHidden()
            for index in range(dialog.dictionary_tree.topLevelItemCount())
        ]
        self.assertEqual(visible, [False, True])
        self.assertIn("Português", dialog.active_summary.text())

    def test_dialog_exposes_empty_progress_and_independent_item_states(self):
        dialog = DictionaryManagerDialog()
        dialog.set_installed_only([], loading=False)
        dialog.filter_combo.setCurrentIndex(
            dialog.filter_combo.findData("installed")
        )
        self.assertFalse(dialog.empty_label.isHidden())
        self.assertIn("installed", dialog.empty_label.text().lower())

        snapshot = DictionaryCatalogSnapshot(
            entries=(
                self._entry("one"),
                self._entry("two"),
            ),
            revision="test",
            fetched_at="2026-08-17T00:00:00+00:00",
        )
        states = [
            DictionaryState("one", "One", False, False, False, True),
            DictionaryState("two", "Two", False, False, False, True),
        ]
        dialog.set_catalog(snapshot, states)
        dialog.filter_combo.setCurrentIndex(dialog.filter_combo.findData("all"))
        first = dialog.dictionary_tree.topLevelItem(0)
        second = dialog.dictionary_tree.topLevelItem(1)
        dialog.dictionary_tree.setCurrentItem(first)
        first.setSelected(True)
        dialog.set_download_busy("one", True)
        self.assertFalse(dialog.cancel_download_button.isHidden())
        dialog.set_download_progress("one", 5, 10)
        self.assertEqual(dialog.progress_bar.value(), 5)

        dialog.dictionary_tree.clearSelection()
        dialog.dictionary_tree.setCurrentItem(second)
        second.setSelected(True)
        self.assertTrue(dialog.install_button.isEnabled())
        self.assertTrue(dialog.cancel_download_button.isHidden())

        requested = []
        dialog.install_requested.connect(requested.append)
        dialog.set_download_busy("one", False)
        first.setSelected(True)
        second.setSelected(True)
        dialog._selection_changed(second, first)
        dialog._request_install()
        self.assertEqual(requested, ["one", "two"])

    @staticmethod
    def _entry(code):
        payload = code.encode()
        return DictionaryCatalogEntry(
            code=code,
            filename=f"{code}.bdic",
            size=len(payload),
            sha256=sha256(payload).hexdigest(),
            source_revision="a" * 40,
            source="test",
        )

    def test_settings_exposes_one_shared_manager_action_without_network(self):
        from zapzap.features.settings.pages.language_downloads.controller import (
            LanguageDownloadSettingsController,
        )

        model = SimpleNamespace(
            spellcheck_enabled=True,
            list_dictionary_options=lambda: [
                SimpleNamespace(code="pt_BR", label="Portuguese (Brazil)")
            ],
            get_selected_dictionaries=lambda: ["pt_BR"],
            get_download_path=lambda: "/downloads",
            list_available_languages=lambda: [],
            get_current_language=lambda: "system",
        )

        with (
            patch(
                "zapzap.features.settings.pages.language_downloads.controller."
                "LanguageDownloadSettingsModel",
                return_value=model,
            ),
            patch.object(DictionaryService, "fetch_catalog") as fetch,
        ):
            page = LanguageDownloadSettingsController()

        self.assertEqual(page.btn_manage_dictionaries.text(), "Manage…")
        self.assertTrue(page.btn_manage_dictionaries.accessibleDescription())
        fetch.assert_not_called()

    def test_package_catalog_hides_management_and_cannot_start_catalog_network(self):
        from zapzap.features.settings.pages.language_downloads.controller import (
            LanguageDownloadSettingsController,
        )

        model = SimpleNamespace(
            spellcheck_enabled=True,
            list_dictionary_options=lambda: [],
            get_selected_dictionaries=lambda: [],
            get_download_path=lambda: "/downloads",
            list_available_languages=lambda: [],
            get_current_language=lambda: "system",
        )
        with (
            patch(
                "zapzap.features.settings.pages.language_downloads.controller."
                "LanguageDownloadSettingsModel",
                return_value=model,
            ),
            patch.object(
                DictionariesManager,
                "is_management_available",
                return_value=False,
            ),
            patch(
                "zapzap.features.dictionaries.dictionary_manager.DictionaryService"
            ) as service,
        ):
            page = LanguageDownloadSettingsController()
            opened = open_dictionary_manager(page)

        self.assertTrue(page.manage_dictionaries_row.isHidden())
        self.assertFalse(opened)
        service.assert_not_called()


if __name__ == "__main__":
    unittest.main()
