#!/bin/sh

set -eu

ARCH="$(uname -m)"

export ARCH
export OUTPATH="./dist"

# Hooks
export ADD_HOOKS="self-updater.hook"

# AppImageUpdate
export UPINFO="gh-releases-zsync|${GITHUB_REPOSITORY%/*}|${GITHUB_REPOSITORY#*/}|latest|*${ARCH}*.AppImage.zsync"

# Metadata
export ICON="/usr/share/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg"
export DESKTOP="/usr/share/applications/com.rtosta.zapzap.desktop"

# Qt / Python deployment
export DEPLOY_OPENGL=1
export DEPLOY_VULKAN=1
export DEPLOY_PIPEWIRE=1
export DEPLOY_PYTHON=1

export DEPLOY_QT=1
export QT_DIR=qt6
export DEPLOY_QT_WEB_ENGINE=1

mkdir -p "${OUTPATH}"

echo "Arquitetura: ${ARCH}"
echo "Gerando AppImage AnyLinux..."

# Cria AppDir e coleta dependências
quick-sharun \
    /usr/bin/zapzap \
    /usr/lib/libQt6Network.so*

# Converte AppDir em AppImage
quick-sharun --make-appimage

# Renomeia para evitar conflito com o AppImage tradicional
for file in "${OUTPATH}"/*.AppImage; do
    [ -f "$file" ] || continue

    base="$(basename "$file" .AppImage)"
    mv "$file" "${OUTPATH}/${base}-anylinux.AppImage"
done

# Renomeia zsync correspondente
for file in "${OUTPATH}"/*.zsync; do
    [ -f "$file" ] || continue

    base="$(basename "$file" .zsync)"
    mv "$file" "${OUTPATH}/${base}-anylinux.zsync"
done

echo
echo "Arquivos gerados:"
ls -lh "${OUTPATH}"

# Opcional:
# quick-sharun --test "${OUTPATH}"/*.AppImage