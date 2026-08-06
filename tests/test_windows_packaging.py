from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WINDOWS_WORKFLOW = (
    REPOSITORY_ROOT / ".github" / "workflows" / "build-windows.yml"
)
WINDOWS_BUILD_SCRIPT = (
    REPOSITORY_ROOT / ".github" / "packaging" / "windows" / "build.ps1"
)
README = REPOSITORY_ROOT / "README.md"


class WindowsPackagingTest(unittest.TestCase):
    def test_workflow_builds_native_x86_64_and_arm64_artifacts(self):
        workflow = WINDOWS_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("runner: windows-latest", workflow)
        self.assertIn("python_arch: x64", workflow)
        self.assertIn("artifact_arch: x86_64", workflow)
        self.assertIn("runner: windows-11-arm", workflow)
        self.assertIn("python_arch: arm64", workflow)
        self.assertIn("artifact_arch: arm64", workflow)
        self.assertIn("architecture: ${{ matrix.python_arch }}", workflow)

    def test_workflow_uses_architecture_in_build_and_upload_names(self):
        workflow = WINDOWS_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn(
            'build.ps1 -Architecture "${{ matrix.artifact_arch }}"',
            workflow,
        )
        self.assertIn("ZapZap-Windows-${{ matrix.artifact_arch }}", workflow)
        artifact_pattern = (
            "dist/ZapZap-*-windows-${{ matrix.artifact_arch }}.exe"
        )
        self.assertEqual(workflow.count(artifact_pattern), 2)

    def test_build_script_rejects_mismatched_python_architecture(self):
        script = WINDOWS_BUILD_SCRIPT.read_text(encoding="utf-8")

        self.assertIn('[ValidateSet("x86_64", "arm64")]', script)
        self.assertIn("platform.machine()", script)
        self.assertIn("$RuntimeArchitecture -notin", script)
        self.assertIn(
            '"dist/ZapZap-$Version-windows-$Architecture.exe"',
            script,
        )

    def test_readme_lists_both_native_windows_architectures(self):
        readme = README.read_text(encoding="utf-8")

        self.assertIn("| Windows | EXE (x86_64, ARM64) |", readme)


if __name__ == "__main__":
    unittest.main()
