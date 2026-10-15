"""Execute the Mac spec with build fakes; never submit an OS notification."""
import ctypes
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / ".github" / "packaging" / "macos" / "ZapZap.spec"


class MacosNotificationPackagingTests(unittest.TestCase):
    def run_spec(self, root):
        calls = {}
        hooks = ModuleType("PyInstaller.utils.hooks")
        hooks.collect_submodules = lambda package: [package + ".sentinel"]

        def build(kind):
            def invoke(*args, **kwargs):
                calls[kind] = (args, kwargs)
                return SimpleNamespace(pure=[], scripts=[], binaries=[], datas=[])
            return invoke

        namespace = {
            "SPECPATH": str(root / ".github" / "packaging" / "macos"),
            **{name: build(name) for name in ("Analysis", "PYZ", "EXE", "COLLECT", "BUNDLE")},
        }
        with patch.dict(sys.modules, {"PyInstaller.utils.hooks": hooks}):
            exec(compile(SPEC.read_text(encoding="utf-8"), str(SPEC), "exec"), namespace)
        return calls

    def fixture(self, directory, *, bridge):
        root = Path(directory).resolve()
        (root / "zapzap").mkdir()
        (root / "zapzap" / "__init__.py").write_text("__version__ = '7.5.1'\n")
        if bridge:
            (root / "build" / "native").mkdir(parents=True)
            (root / "build" / "native" / "libZapZapNotifications.dylib").write_bytes(b"fixture")
        return root

    def test_spec_is_relocatable_and_preserves_resources_and_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory, bridge=True)
            calls = self.run_spec(root)
        analysis = calls["Analysis"][1]
        self.assertEqual(analysis["pathex"], [str(root)])
        self.assertEqual(analysis["binaries"][0][1], "zapzap/features/notifications")
        self.assertEqual({destination for _, destination in analysis["datas"]}, {
            "zapzap/po", "zapzap/assets", "zapzap/features/browser/web/scripts",
        })
        self.assertIn("zapzap.features.settings.pages.sentinel", analysis["hiddenimports"])
        self.assertIn("zapzap.features.notifications.macos_native_notifications", analysis["hiddenimports"])
        bundle = calls["BUNDLE"][1]
        self.assertEqual(bundle["bundle_identifier"], "ZapZap")
        self.assertEqual(bundle["info_plist"]["NSUserActivityTypes"], ["INSendMessageIntent"])
        self.assertEqual(bundle["info_plist"]["CFBundleVersion"], "7.5.1")
        self.assertFalse(calls["EXE"][1]["console"])

    def test_missing_compiled_bridge_fails_before_analysis(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory, bridge=False)
            with self.assertRaisesRegex(SystemExit, "build-native.sh"):
                self.run_spec(root)

    @unittest.skipUnless(sys.platform == "darwin", "native Mac library load")
    def test_compiled_native_library_has_the_complete_public_abi(self):
        library = ROOT / "build" / "native" / "libZapZapNotifications.dylib"
        if not library.is_file():
            self.skipTest("run build-native.sh first")
        bridge = ctypes.CDLL(str(library))
        for symbol in ("zn_install", "zn_send", "zn_send_message", "zn_remove"):
            self.assertTrue(callable(getattr(bridge, symbol)))
