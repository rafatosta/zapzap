import os
import shutil
import subprocess
import tarfile

from pathlib import Path
from urllib.request import urlretrieve


class AppImageBuilder:
    def __init__(self, version: str):
        if not version:
            raise ValueError(
                "Tag da versão não definida"
            )

        self.version = version

        # ==================================================
        # WORKDIR TEMPORÁRIO
        # ==================================================

        self.workdir = Path(".appimage-builder")

        # ==================================================
        # DIST FINAL (PERSISTENTE)
        # ==================================================

        self.dist_dir = Path("dist")

        # ==================================================
        # DIST TEMPORÁRIO DO PYINSTALLER
        # ==================================================

        self.temp_dist_dir = (
            self.workdir / "dist"
        )

        # ==================================================
        # APPDIR
        # ==================================================

        self.appdir = (
            self.temp_dist_dir / "zapzap"
        )

        # ==================================================
        # APPIMAGETOOL
        # ==================================================

        self.appimagetool = (
            self.workdir /
            "appimagetool-x86_64.AppImage"
        )

        # ==================================================
        # SOURCE
        # ==================================================

        self.code_zip = (
            self.workdir /
            f"{version}.tar.gz"
        )

        self.code_folder = (
            self.workdir /
            f"zapzap-{version}"
        )

    # ======================================================
    # RUN
    # ======================================================

    def run(self):
        self.prepare()
        self.download_appimagetool()
        self.download_source()
        self.extract_source()
        self.create_spec()
        self.build_pyinstaller()
        self.create_apprun()
        self.copy_resources()
        self.download_dictionaries()
        self.build_appimage()
        self.cleanup()

    # ======================================================
    # PREPARE
    # ======================================================

    def prepare(self):
        print(
            f"Construção para a tag: "
            f"{self.version}"
        )

        self.workdir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.dist_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    # ======================================================
    # APPIMAGETOOL
    # ======================================================

    def download_appimagetool(self):
        if self.appimagetool.exists():
            print(
                f"{self.appimagetool} "
                f"já existe"
            )
            return

        print("Baixando appimagetool...")

        urlretrieve(
            (
                "https://github.com/"
                "AppImage/AppImageKit/"
                "releases/download/"
                "continuous/"
                "appimagetool-x86_64.AppImage"
            ),
            self.appimagetool
        )

        self.appimagetool.chmod(0o755)

    # ======================================================
    # SOURCE
    # ======================================================

    def download_source(self):
        if self.version == "dev":
            print(
                "Modo desenvolvimento detectado"
            )

            print(
                "Usando código local "
                "do repositório"
            )

            shutil.copytree(
                Path.cwd(),
                self.code_folder,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(
                    ".git",
                    ".venv",
                    "__pycache__",
                    "dist",
                    "build",
                    ".appimage-builder"
                )
            )

            return

        if self.code_zip.exists():
            print(
                f"{self.code_zip} "
                f"já existe"
            )
            return

        print("Baixando código fonte...")

        urlretrieve(
            (
                "https://github.com/"
                "rafatosta/zapzap/"
                "archive/refs/tags/"
                f"{self.version}.tar.gz"
            ),
            self.code_zip
        )

    # ======================================================
    # EXTRACT
    # ======================================================

    def extract_source(self):
        if self.version == "dev":
            return

        if self.code_folder.exists():
            print(
                f"{self.code_folder} "
                f"já existe"
            )
            return

        print("Extraindo código fonte...")

        with tarfile.open(
            self.code_zip,
            "r:gz"
        ) as tar:
            tar.extractall(self.workdir)

    # ======================================================
    # SPEC
    # ======================================================

    def create_spec(self):
        spec_file = (
            self.code_folder /
            "zapzap.spec"
        )

        print(f"Criando {spec_file}")

        spec_content = r"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['./zapzap/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('zapzap', 'zapzap')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='zapzap',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='zapzap'
)
"""

        spec_file.write_text(spec_content)

    # ======================================================
    # PYINSTALLER
    # ======================================================

    def build_pyinstaller(self):
        print("Executando PyInstaller...")

        result = subprocess.run(
            [
                "pyinstaller",
                "zapzap.spec",
                "-y",
                "--distpath",
                str(
                    self.temp_dist_dir.resolve()
                ),
                "--workpath",
                str(
                    (
                        self.workdir /
                        "build"
                    ).resolve()
                )
            ],
            cwd=self.code_folder,
            text=True,
            capture_output=True
        )

        print(result.stdout)
        print(result.stderr)

        if result.returncode != 0:
            raise RuntimeError(
                "Falha no PyInstaller"
            )

    # ======================================================
    # APPRUN
    # ======================================================

    def create_apprun(self):
        print("Criando AppRun...")

        apprun = self.appdir / "AppRun"

        apprun.write_text(
            (
                '#!/bin/sh\n\n'
                'cd "$(dirname "$0")"\n\n'
                '# Workaround para QtWebEngine em AppImage\n'
                'if [ -z "$QTWEBENGINE_CHROMIUM_FLAGS" ]; then\n'
                '    export QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu"\n'
                'fi\n\n'
                'exec ./zapzap "$@"\n'
            )
        )

        apprun.chmod(0o755)

    # ======================================================
    # RESOURCES
    # ======================================================

    def copy_resources(self):
        print("Copiando recursos...")

        icon_src = (
            self.code_folder /
            "share/icons/"
            "com.rtosta.zapzap.svg"
        )

        desktop_src = (
            self.code_folder /
            "share/applications/"
            "com.rtosta.zapzap.desktop"
        )

        shutil.copy(
            icon_src,
            (
                self.appdir /
                "com.rtosta.zapzap.svg"
            )
        )

        shutil.copy(
            desktop_src,
            (
                self.appdir /
                "zapzap.desktop"
            )
        )

    # ======================================================
    # DICTIONARIES
    # ======================================================

    def download_dictionaries(self):
        print("Baixando dicionários...")

        zip_path = (
            self.workdir /
            "qtwebengine_dictionaries.zip"
        )

        urlretrieve(
            (
                "https://github.com/"
                "rafatosta/"
                "qtwebengine_dictionaries/"
                "archive/refs/heads/main.zip"
            ),
            zip_path
        )

        subprocess.run(
            [
                "unzip",
                "-o",
                str(zip_path),
                "-d",
                str(self.workdir)
            ],
            check=True
        )

        source_dir = (
            self.workdir /
            "qtwebengine_dictionaries-main"
        )

        target_dir = (
            self.appdir /
            "qtwebengine_dictionaries"
        )

        target_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        for file in source_dir.glob("*.bdic"):
            shutil.copy(
                file,
                target_dir / file.name
            )

    # ======================================================
    # APPIMAGE
    # ======================================================

    def build_appimage(self):
        print("Gerando AppImage...")

        env = os.environ.copy()
        env["ARCH"] = "x86_64"

        result = subprocess.run(
            [
                str(self.appimagetool),
                str(self.appdir)
            ],
            env=env,
            text=True,
            capture_output=True
        )

        print(result.stdout)
        print(result.stderr)

        if result.returncode != 0:
            raise RuntimeError(
                "Falha ao gerar AppImage"
            )

        generated_appimages = list(
            Path(".").glob("*.AppImage")
        )

        print("AppImages encontrados:")
        print(generated_appimages)

        if not generated_appimages:
            raise RuntimeError(
                "Nenhum AppImage foi gerado"
            )

        appimage_file = (
            generated_appimages[0]
        )

        final_path = (
            self.dist_dir /
            appimage_file.name
        )

        shutil.move(
            str(appimage_file),
            str(final_path)
        )

        print(
            f"AppImage movido para: "
            f"{final_path}"
        )

    # ======================================================
    # CLEANUP
    # ======================================================

    def cleanup(self):
        print(
            "Removendo arquivos temporários..."
        )

        shutil.rmtree(
            self.workdir,
            ignore_errors=True
        )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso:")
        print(
            "python -m "
            "builders.appimage_builder "
            "<tag>"
        )

        sys.exit(1)

    builder = AppImageBuilder(sys.argv[1])
    builder.run()