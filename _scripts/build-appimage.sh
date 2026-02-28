#!/usr/bin/env bash
set -e

clear

if [ $# -eq 0 ]; then
    echo "Tag da versão não definida"
    exit 1
fi

tag=$1
WORKDIR=".appimage-builder"
VENV_DIR=".venv-build"

echo "Construção para a tag: $tag"

# -----------------------------
# Verificar Python 3.12
# -----------------------------
if ! command -v python3.12 &> /dev/null; then
    echo "Python 3.12 não encontrado. Instale antes de continuar."
    exit 1
fi

# -----------------------------
# Criar ambiente isolado
# -----------------------------
if [ ! -d "$VENV_DIR" ]; then
    python3.12 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install \
    pyinstaller==6.6.0 \
    setuptools \
    wheel

# -----------------------------
# Preparar diretórios
# -----------------------------
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"

# -----------------------------
# Download AppImageTool
# -----------------------------
appimagetool="$WORKDIR/appimagetool-x86_64.AppImage"

if [ ! -f "$appimagetool" ]; then
    wget -O "$appimagetool" \
    https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x "$appimagetool"
fi

# -----------------------------
# Download código
# -----------------------------
codeZip="$WORKDIR/$tag.tar.gz"

wget -O "$codeZip" \
https://github.com/rafatosta/zapzap/archive/refs/tags/$tag.tar.gz

tar -xzf "$codeZip" -C "$WORKDIR"

codeFolder="$WORKDIR/zapzap-$tag"

# -----------------------------
# Criar .spec
# -----------------------------
spec_file="$codeFolder/zapzap.spec"

cat > "$spec_file" <<EOF
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['./zapzap/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('zapzap', 'zapzap')],
    hiddenimports=[],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='zapzap',
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='zapzap',
)
EOF

# -----------------------------
# Build PyInstaller
# -----------------------------
pyinstaller "$spec_file" \
    --distpath "$WORKDIR/dist" \
    --workpath "$WORKDIR/build" \
    --clean \
    -y

APPDIR="$WORKDIR/dist/zapzap"

# -----------------------------
# AppRun
# -----------------------------
cat > "$APPDIR/AppRun" <<EOF
#!/bin/sh
cd "\$(dirname "\$0")"
exec ./zapzap
EOF

chmod +x "$APPDIR/AppRun"

# -----------------------------
# Copiar assets
# -----------------------------
cp "$codeFolder/share/icons/com.rtosta.zapzap.svg" \
   "$APPDIR/com.rtosta.zapzap.svg"

cp "$codeFolder/share/applications/com.rtosta.zapzap.desktop" \
   "$APPDIR/zapzap.desktop"

# -----------------------------
# QtWebEngine dictionaries
# -----------------------------
wget https://github.com/rafatosta/qtwebengine_dictionaries/archive/refs/heads/main.zip \
-O "$WORKDIR/qtwebengine_dictionaries.zip"

unzip -o "$WORKDIR/qtwebengine_dictionaries.zip" -d "$WORKDIR"

mkdir -p "$APPDIR/qtwebengine_dictionaries"

cp "$WORKDIR/qtwebengine_dictionaries-main"/*.bdic \
   "$APPDIR/qtwebengine_dictionaries"

# -----------------------------
# Gerar AppImage
# -----------------------------
ARCH=x86_64 "$appimagetool" "$APPDIR"

echo ""
echo "Build concluído com sucesso."