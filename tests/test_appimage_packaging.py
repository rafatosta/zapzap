import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
NORMALIZE_SCRIPT = (
    REPOSITORY_ROOT / ".github" / "packaging" / "appimage" / "normalize.sh"
)


class AppImagePackagingTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.dist = self.root / "dist"
        self.bin_dir = self.root / "bin"
        self.dist.mkdir()
        self.bin_dir.mkdir()
        (self.root / "version").write_text("7.1\n", encoding="utf-8")

        fake_zsyncmake = self.bin_dir / "zsyncmake"
        fake_zsyncmake.write_text(
            textwrap.dedent(
                """\
                #!/bin/sh
                set -eu

                filename=""
                url=""
                output=""

                while [ "$#" -gt 0 ]; do
                    case "$1" in
                        -e)
                            shift
                            ;;
                        -f)
                            filename="$2"
                            shift 2
                            ;;
                        -u)
                            url="$2"
                            shift 2
                            ;;
                        -o)
                            output="$2"
                            shift 2
                            ;;
                        *)
                            input="$1"
                            shift
                            ;;
                    esac
                done

                length="$(wc -c < "$input")"
                {
                    printf 'zsync: 0.6.5\\n'
                    printf 'Filename: %s\\n' "$filename"
                    printf 'Blocksize: 2048\\n'
                    printf 'Length: %s\\n' "$length"
                    printf 'Hash-Lengths: 1,2,4\\n'
                    printf 'URL: %s\\n' "$url"
                    printf 'SHA-1: fake\\n\\n'
                    printf 'checksums'
                } > "$output"
                """
            ),
            encoding="utf-8",
        )
        fake_zsyncmake.chmod(0o755)

    def run_normalize(self):
        env = os.environ.copy()
        env["HOME"] = str(self.root)
        env["PATH"] = f"{self.bin_dir}{os.pathsep}{env['PATH']}"
        return subprocess.run(
            [str(NORMALIZE_SCRIPT), "x86_64"],
            cwd=self.root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_regenerates_zsync_after_appimage_gets_final_name(self):
        old_appimage = self.dist / "ZapZap-7.1-anylinux-x86_64.AppImage"
        old_zsync = self.dist / f"{old_appimage.name}.zsync"
        old_appimage.write_bytes(b"appimage")
        old_zsync.write_text(
            "Filename: ZapZap-7.1-anylinux-x86_64.AppImage\n"
            "URL: ZapZap-7.1-anylinux-x86_64.AppImage\n",
            encoding="utf-8",
        )

        result = self.run_normalize()

        self.assertEqual(result.returncode, 0, result.stderr)
        final_name = "ZapZap-7.1-linux-x86_64.AppImage"
        final_appimage = self.dist / final_name
        final_zsync = self.dist / f"{final_name}.zsync"
        self.assertEqual(final_appimage.read_bytes(), b"appimage")
        self.assertFalse(old_appimage.exists())
        self.assertFalse(old_zsync.exists())
        zsync_header = final_zsync.read_bytes().split(b"\n\n", 1)[0].decode()
        self.assertIn(f"Filename: {final_name}", zsync_header)
        self.assertIn(f"URL: {final_name}", zsync_header)
        self.assertNotIn("anylinux", zsync_header)

    def test_fails_when_generated_zsync_is_missing(self):
        (self.dist / "ZapZap-7.1-anylinux-x86_64.AppImage").write_bytes(
            b"appimage"
        )

        result = self.run_normalize()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "Expected exactly one zsync control file in dist, found 0.",
            result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
