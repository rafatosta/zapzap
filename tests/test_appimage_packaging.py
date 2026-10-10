from pathlib import Path
import subprocess
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MAKE_APPIMAGE_SCRIPT = (
    REPOSITORY_ROOT
    / ".github"
    / "packaging"
    / "appimage"
    / "scripts"
    / "make-appimage.sh"
)
GET_DEPENDENCIES_SCRIPT = (
    REPOSITORY_ROOT
    / ".github"
    / "packaging"
    / "appimage"
    / "scripts"
    / "get-dependencies.sh"
)
APPIMAGE_WORKFLOW = (
    REPOSITORY_ROOT / ".github" / "workflows" / "build-appimage.yml"
)
NORMALIZE_SCRIPT = (
    REPOSITORY_ROOT / ".github" / "packaging" / "appimage" / "normalize.sh"
)


class AppImagePackagingTest(unittest.TestCase):
    def test_webengine_paths_and_missing_bundle_data(self):
        script = MAKE_APPIMAGE_SCRIPT.read_text(encoding="utf-8")
        start = script.index("# quick-sharun collects WebEngine data")
        end = script.index("\nEOF", start) + len("\nEOF")
        validation = script[start:end]
        self.assertLess(end, script.index("quick-sharun --make-appimage"))
        resources = (
            "qtwebengine_resources.pak",
            "qtwebengine_resources_100p.pak",
            "qtwebengine_resources_200p.pak",
            "qtwebengine_devtools_resources.pak",
            "v8_context_snapshot.bin",
        )
        with tempfile.TemporaryDirectory(prefix="appimage paths ") as temporary:
            root = Path(temporary)
            resource_dir = root / "lib/qt6/resources"
            resource_dir.mkdir(parents=True)
            required = [resource_dir / name for name in resources]
            required.append(root / "lib/qt6/translations/qtwebengine_locales/en-US.pak")
            helper = root / "bin/QtWebEngineProcess"
            required.append(helper)
            for path in required:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture", encoding="utf-8")
            helper.chmod(0o755)

            def run_validation():
                return subprocess.run(
                    ["sh", "-eu", "-c", 'APPDIR="$1"\n' + validation, "sh", str(root)],
                    capture_output=True, text=True, check=False,
                )

            result = run_validation()
            self.assertEqual(result.returncode, 0, result.stderr)
            environment = (root / ".env").read_text(encoding="utf-8")
            self.assertIn("QTWEBENGINE_RESOURCES_PATH=${SHARUN_DIR}/lib/qt6/resources", environment)
            self.assertIn("QTWEBENGINE_LOCALES_PATH=${SHARUN_DIR}/lib/qt6/translations/qtwebengine_locales", environment)
            self.assertIn("QTWEBENGINEPROCESS_PATH=${SHARUN_DIR}/bin/QtWebEngineProcess", environment)
            self.assertNotIn(str(root), environment)
            for path in required:
                with self.subTest(missing=path.name):
                    path.write_text("", encoding="utf-8")
                    if path == helper:
                        helper.chmod(0o644)
                    self.assertNotEqual(run_validation().returncode, 0)
                    path.write_text("fixture", encoding="utf-8")
                    helper.chmod(0o755)

    def test_ffmpeg_uses_the_same_repository_transaction_as_qt_webengine(self):
        script = GET_DEPENDENCIES_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("pacman -Syu --noconfirm", script)
        self.assertIn("    ffmpeg \\", script)
        self.assertIn(
            "get-debloated-pkgs --add-common --prefer-nano",
            script,
        )
        self.assertNotIn(
            "get-debloated-pkgs --add-common --prefer-nano ffmpeg-mini",
            script,
        )

    def test_qt_webengine_dependencies_are_checked_before_deployment(self):
        script = MAKE_APPIMAGE_SCRIPT.read_text(encoding="utf-8")
        dependency_check = "sed -n '/not found/p'"
        deployment = "quick-sharun \\"

        self.assertIn("/usr/lib/libQt6WebEngineWidgets.so", script)
        self.assertIn("/usr/lib/libQt6WebEngineCore.so", script)
        self.assertIn(dependency_check, script)
        self.assertLess(
            script.index(dependency_check),
            script.index(deployment),
        )

    def test_final_name_is_defined_before_quick_sharun_builds_artifacts(self):
        script = MAKE_APPIMAGE_SCRIPT.read_text(encoding="utf-8")
        outname = (
            'export OUTNAME="ZapZap-${VERSION}-linux-${ARCH}.AppImage"'
        )

        self.assertIn('VERSION="$(cat ~/version)"', script)
        self.assertIn(outname, script)
        self.assertLess(
            script.index(outname),
            script.index("quick-sharun --make-appimage"),
        )
        self.assertIn("export UPINFO=", script)

    def test_workflow_does_not_rename_generated_artifacts(self):
        workflow = APPIMAGE_WORKFLOW.read_text(encoding="utf-8")

        self.assertFalse(NORMALIZE_SCRIPT.exists())
        self.assertNotIn("normalize.sh", workflow)
        self.assertNotIn("Normalize artifact names", workflow)


if __name__ == "__main__":
    unittest.main()
