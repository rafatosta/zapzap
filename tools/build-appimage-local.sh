clear 

# Define a pasta de trabalho
WORKDIR=".appimage-builder-preview"
mkdir -p "$WORKDIR"


# Download do AppImageTool-x86_64
appimagetool="$WORKDIR/appimagetool-x86_64.AppImage"
echo $appimagetool 

if [ -f "$appimagetool" ]; then
    echo "O arquivo $appimagetool existe."
else
    echo "O arquivo $appimagetool não existe."
    echo "Downloading appimagetool-x86_64..."
    wget -O "$appimagetool" https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x $appimagetool
fi

# Extrai o código fonte

codeFolder="../zapzap"

echo "$codeFolder"
ls "$codeFolder"

# Cria arquivo .spec
spec_file="$codeFolder/zapzap.spec"
echo "Criado zapzap.spec: $spec_file"

spec_txt="# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['./zapzap/__main__.py'],
             pathex=[],
             binaries=[],
             datas=[('zapzap', 'zapzap')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='zapzap',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='zapzap')"

# Adiciona o novo conteúdo ao arquivo
echo "$spec_txt" > "$spec_file"

# Construção pelo Pyinstaller
echo "$spec_file" -y --distpath "$WORKDIR/dist" --workpath "$WORKDIR/build" --specpath "$WORKDIR"
pyinstaller "$spec_file" -y --distpath $WORKDIR/dist --workpath $WORKDIR/build

## AppRun file
appRun="#!/bin/sh\n\ncd \"\$(dirname \"\$0\")\"\nexec ./zapzap"

mkdir -p "$WORKDIR/dist/zapzap"
echo -e "$appRun" > "$WORKDIR/dist/zapzap/AppRun"
chmod +x "$WORKDIR/dist/zapzap/AppRun"

## build.sh file
build_file="# detect machine's architecture
export ARCH=\$(uname -m)

# get the missing tools if necessary
if [ ! -d ../build ]; then mkdir ../build; fi
if [ ! -x ../build/appimagetool-\$ARCH.AppImage ]; then
  curl -L -o ../build/appimagetool-\$ARCH.AppImage https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-\$ARCH.AppImage
  chmod a+x ../build/appimagetool-\$ARCH.AppImage 
fi
# the build command itself:
../build/appimagetool-\$ARCH.AppImage \$PWD

# move result in build folder
mv hello-world-appimage-*-\$ARCH.AppImage ../build"

echo -e "$build_file" > "$WORKDIR/dist/zapzap/build.sh"
chmod +x "$WORKDIR/dist/zapzap/build.sh"

# Copiar icone
cp "$codeFolder/share/icons/com.rtosta.zapzap.svg" "$WORKDIR/dist/zapzap/com.rtosta.zapzap.svg"

# Copiar .desktop
echo "$codeFolder/share/applications/com.rtosta.zapzap.desktop" "$WORKDIR/dist/zapzap/zapzap.desktop"
cp "$codeFolder/share/applications/com.rtosta.zapzap.desktop" "$WORKDIR/dist/zapzap/zapzap.desktop"


# Download do dicionário

if [ -f "$WORKDIR/qtwebengine_dictionaries" ]; then
    echo "O arquivo $WORKDIR/qtwebengine_dictionaries existe."
else
    wget https://github.com/rafatosta/qtwebengine_dictionaries/archive/refs/heads/main.zip -O $WORKDIR/qtwebengine_dictionaries.zip
    unzip -o "$WORKDIR/qtwebengine_dictionaries.zip" -d "$WORKDIR"
fi

# Copiar o dicionário
mkdir -p "$WORKDIR/dist/zapzap/qtwebengine_dictionaries"

echo "$WORKDIR/qtwebengine_dictionaries-main" "$WORKDIR/dist/zapzap/qtwebengine_dictionaries"
cp "$WORKDIR/qtwebengine_dictionaries-main"/*.bdic -r "$WORKDIR/dist/zapzap/qtwebengine_dictionaries"


ARCH=x86_64 "$appimagetool" "$WORKDIR/dist/zapzap/"

./ZapZap-x86_64.AppImage