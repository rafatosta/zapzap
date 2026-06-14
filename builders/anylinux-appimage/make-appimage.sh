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
DESKTOP_FILE="$(find . -name "com.rtosta.zapzap.desktop" | head -n1)"
ICON_FILE="$(find . -name "com.rtosta.zapzap.svg" | head -n1)"

echo "Desktop: ${DESKTOP_FILE}"
echo "Icon: ${ICON_FILE}"

export DESKTOP="${DESKTOP_FILE}"
export ICON="${ICON_FILE}"

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

ZAPZAP_BIN="$(command -v zapzap)"

if [ -z "${ZAPZAP_BIN}" ]; then
    echo "Erro: executável zapzap não encontrado."
    exit 1
fi

echo "Executável encontrado em: ${ZAPZAP_BIN}"

# Cria AppDir e coleta dependências
quick-sharun \
    "${ZAPZAP_BIN}" \
    /usr/lib/libQt6Network.so*

# Converte AppDir em AppImage
quick-sharun --make-appimage

echo
echo "Arquivos gerados:"
ls -lh "${OUTPATH}"

# Opcional:
# quick-sharun --test "${OUTPATH}"/*.AppImage