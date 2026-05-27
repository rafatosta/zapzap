import shutil
import subprocess
import tarfile
from pathlib import Path
from urllib.request import urlretrieve


class AppImageBuilder:
    def __init__(self, version: str):
        if not version:
            raise ValueError("Tag da versão não definida")

        self.version = version
        self.workdir = Path(".appimage-builder")

        self.appimagetool = (
            self.workdir / "appimagetool-x86_64.AppImage"
        )

        self.code_zip = self.workdir / f"{version}.tar.gz"
        self.code_folder = self.workdir / f"zapzap-{version}"

        self.dist_dir = self.workdir / "dist"
        self.appdir = self.dist_dir / "zapzap"

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

    def prepare(self):
        print(f"Construção para a tag: {self.version}")
        self.workdir.mkdir(exist_ok=True)

    def download_appimagetool(self):
        if self.appimagetool.exists():
            print(f"{self.appimagetool} já existe")
            return

        print("Baixando appimagetool...")
        urlretrieve(
            "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage",
            self.appimagetool
        )

        self.appimagetool.chmod(0o755)

    def download_source(self):
        if self.code_zip.exists():
            print(f"{self.code_zip} já existe")
            return

        print("Baixando código fonte...")
        urlretrieve(
            f"https://github.com/rafatosta/zapzap/archive/refs/tags/{self.version}.tar.gz",
            self.code_zip
        )

    def extract_source(self):
        if self.code_folder.exists():
            print(f"{self.code_folder} já existe")
            return

        print("Extraindo código fonte...")

        with tarfile.open(self.code_zip, "r:gz") as tar:
            tar.extractall(self.workdir)

    def create_spec(self):
        spec_file = self.code_folder / "zapzap.spec"

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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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

    def build_pyinstaller(self):
        spec_file = self.code_folder / "zapzap.spec"

        print("Executando PyInstaller...")

        result = subprocess.run(
            [
                "pyinstaller",
                "zapzap.spec",
                "-y",
                "--distpath",
                str(self.dist_dir.resolve()),
                "--workpath",
                str((self.workdir / "build").resolve())
            ],
            cwd=self.code_folder,
            text=True,
            capture_output=True
        )

        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            raise RuntimeError("Falha no PyInstaller")

    def create_apprun(self):
        print("Criando AppRun...")

        apprun = self.appdir / "AppRun"

        apprun.write_text(
            '#!/bin/sh\n\ncd "$(dirname "$0")"\nexec ./zapzap\n'
        )

        apprun.chmod(0o755)

    def copy_resources(self):
        print("Copiando recursos...")

        icon_src = (
            self.code_folder /
            "share/icons/com.rtosta.zapzap.svg"
        )

        desktop_src = (
            self.code_folder /
            "share/applications/com.rtosta.zapzap.desktop"
        )

        shutil.copy(icon_src, self.appdir / "com.rtosta.zapzap.svg")
        shutil.copy(desktop_src, self.appdir / "zapzap.desktop")

    def download_dictionaries(self):
        print("Baixando dicionários...")

        zip_path = self.workdir / "qtwebengine_dictionaries.zip"

        urlretrieve(
            "https://github.com/rafatosta/qtwebengine_dictionaries/archive/refs/heads/main.zip",
            zip_path
        )

        subprocess.run(
            ["unzip", "-o", str(zip_path), "-d", str(self.workdir)],
            check=True
        )

        source_dir = self.workdir / "qtwebengine_dictionaries-main"

        target_dir = self.appdir / "qtwebengine_dictionaries"

        target_dir.mkdir(exist_ok=True)

        for file in source_dir.glob("*.bdic"):
            shutil.copy(file, target_dir / file.name)

    def build_appimage(self):
        print("Gerando AppImage...")

        env = dict(**dict(), ARCH="x86_64")

        subprocess.run(
            [
                str(self.appimagetool),
                str(self.appdir)
            ],
            env=env,
            check=True
        )

    def cleanup(self):
        print("Removendo arquivos temporários...")

        shutil.rmtree(self.workdir, ignore_errors=True)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso:")
        print("python build_appimage.py <tag>")
        sys.exit(1)

    builder = AppImageBuilder(sys.argv[1])
    builder.run()