from pathlib import Path
import shutil
import subprocess
import sys


class WindowsBuilder:
    APP_NAME = "ZapZap"

    UI_FILES = [
        ("zapzap/ui/ui_mainwindow.ui", "zapzap/views/ui_mainwindow.py"),
        ("zapzap/ui/ui_page_general.ui", "zapzap/views/ui_page_general.py"),
        ("zapzap/ui/ui_page_network.ui", "zapzap/views/ui_page_network.py"),
    ]

    ADDITIONAL_DATA = [
        ("zapzap/po", "zapzap/po"),
        ("zapzap/ui", "zapzap/ui"),
        ("zapzap/resources", "zapzap/resources"),
        (
            "zapzap/webengine/webrtc_shield.js",
            "zapzap/webengine",
        ),
        (
            "zapzap/webengine/theme_controller.js",
            "zapzap/webengine",
        ),
    ]

    def __init__(self):
        self.root_dir = Path.cwd()

        self.dist_dir = self.root_dir / "dist"
        self.build_dir = self.root_dir / "build"

    def run(self):
        print("# === Windows Builder ===")

        self.compile_ui_files()
        self.clean_previous_build()
        self.run_pyinstaller()
        self.rename_executable()

        print("# === Build concluído com sucesso ===")

    # ==========================================================
    # UI
    # ==========================================================

    def compile_ui_files(self):
        print("# === Compilando arquivos .ui ===")

        for source, target in self.UI_FILES:
            source_path = Path(source)
            target_path = Path(target)

            if not source_path.exists():
                print(f"[IGNORADO] {source}")
                continue

            print(f"{source} -> {target}")

            self.run_pyuic(source_path, target_path)

    def run_pyuic(self, source: Path, target: Path):
        commands = [
            [
                sys.executable,
                "-m",
                "PyQt6.uic.pyuic",
                "-x",
                str(source),
                "-o",
                str(target),
            ],
            [
                "pyuic6",
                "-x",
                str(source),
                "-o",
                str(target),
            ],
        ]

        for command in commands:
            try:
                subprocess.run(command, check=True)
                return

            except Exception:
                continue

        raise RuntimeError(f"Falha ao compilar: {source}")

    # ==========================================================
    # CLEAN
    # ==========================================================

    def clean_previous_build(self):
        print("# === Limpando builds anteriores ===")

        folders = [
            self.dist_dir,
            self.build_dir,
        ]

        for folder in folders:
            if folder.exists():
                shutil.rmtree(folder)

    # ==========================================================
    # PYINSTALLER
    # ==========================================================

    def run_pyinstaller(self):
        print("# === Executando PyInstaller ===")

        command = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--name",
            self.APP_NAME,
            "--onefile",
            "--windowed",
            "--noconfirm",
        ]

        for source, target in self.ADDITIONAL_DATA:
            command.extend(
                [
                    "--add-data",
                    f"{source};{target}",
                ]
            )

        command.append("zapzap/__main__.py")

        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
        )

        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)

            raise RuntimeError(
                "Falha ao executar PyInstaller"
            )

    def rename_executable(self):
        exe_path = self.dist_dir / "ZapZap.exe"

        if not exe_path.exists():
            raise FileNotFoundError(exe_path)

        version = self.get_version()

        final_name = (
            f"ZapZap-{version}-windows-x86_64.exe"
        )

        final_path = self.dist_dir / final_name

        if final_path.exists():
            final_path.unlink()

        exe_path.rename(final_path)

        print(
            f"Executável gerado: {final_path.name}"
        )

    def get_version(self):
        version_file = (
            self.root_dir
            / "zapzap"
            / "__init__.py"
        )

        for line in version_file.read_text(
            encoding="utf-8"
        ).splitlines():
            if line.startswith("__version__"):
                return (
                    line.split("=")[1]
                    .strip()
                    .strip("'\"")
                )

        return "dev"


if __name__ == "__main__":
    WindowsBuilder().run()
