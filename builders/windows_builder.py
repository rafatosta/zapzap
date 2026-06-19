from pathlib import Path
import shutil
import subprocess
import sys

from builders.common import (
    UI_FILES,
    ADDITIONAL_DATA,
    create_build_info,
)


class WindowsBuilder:
    APP_NAME = "ZapZap"

    ICON_FILE = (
        "zapzap/resources/icons/zapzap.ico"
    )

    def __init__(self):
        self.root_dir = Path.cwd()

        self.dist_dir = self.root_dir / "dist"
        self.build_dir = self.root_dir / "build"

    def run(self):
        print("# === Windows Builder ===")

        create_build_info()

        self.compile_ui_files()
        self.clean_previous_build()
        self.run_pyinstaller()
        self.create_zip()

        print("# === Build concluído com sucesso ===")

    # ======================================================
    # UI
    # ======================================================

    def compile_ui_files(self):
        print("# === Compilando arquivos .ui ===")

        for source, target in UI_FILES:
            source_path = Path(source)
            target_path = Path(target)

            if not source_path.exists():
                print(f"[IGNORADO] {source}")
                continue

            self.run_pyuic(
                source_path,
                target_path,
            )

    def run_pyuic(
        self,
        source: Path,
        target: Path,
    ):
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
                subprocess.run(
                    command,
                    check=True,
                )

                return

            except Exception:
                pass

        raise RuntimeError(
            f"Falha ao compilar: {source}"
        )

    # ======================================================
    # CLEAN
    # ======================================================

    def clean_previous_build(self):
        print("# === Limpando builds anteriores ===")

        for folder in (
            self.dist_dir,
            self.build_dir,
        ):
            if folder.exists():
                shutil.rmtree(folder)

    # ======================================================
    # PYINSTALLER
    # ======================================================

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

        icon_path = Path(
            self.ICON_FILE
        )

        if icon_path.exists():
            command.extend(
                [
                    "--icon",
                    str(icon_path),
                ]
            )

        for source, target in ADDITIONAL_DATA:
            command.extend(
                [
                    "--add-data",
                    f"{source};{target}",
                ]
            )

        command.append(
            "zapzap/__main__.py"
        )

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

    # ======================================================
    # ZIP
    # ======================================================

    def create_zip(self):
        print("# === Criando ZIP ===")

        exe_path = (
            self.dist_dir
            / f"{self.APP_NAME}.exe"
        )

        if not exe_path.exists():
            raise FileNotFoundError(
                exe_path
            )

        archive_name = (
            self.dist_dir
            / "ZapZap-Windows-x86_64"
        )

        shutil.make_archive(
            str(archive_name),
            "zip",
            root_dir=self.dist_dir,
            base_dir=".",
        )

        print(
            f"ZIP criado: {archive_name}.zip"
        )


if __name__ == "__main__":
    WindowsBuilder().run()