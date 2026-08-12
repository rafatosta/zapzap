from pathlib import Path
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
