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

APPDIR="./AppDir"
ZAPZAP_BIN="${APPDIR}/usr/bin/zapzap"

if [ ! -x "${ZAPZAP_BIN}" ]; then
    echo "Erro: executável zapzap não encontrado em ${ZAPZAP_BIN}."
    echo "Execute get-dependencies.sh para preparar a instalação em DESTDIR antes de empacotar."
    exit 1
fi

echo "Executável preparado em: ${ZAPZAP_BIN}"

echo
echo "==============================================================="
echo "Criando AppDir"
echo "==============================================================="

# PyQt6 WebEngine carrega dependências Qt em runtime.
# Estas bibliotecas precisam ser passadas explicitamente ao Sharun,
# caso contrário o AppImage fica incompleto.

quick-sharun \
    "${ZAPZAP_BIN}" \
    /usr/lib/libQt6Network.so* \
    /usr/lib/libQt6Widgets.so* \
    /usr/lib/libQt6PrintSupport.so* \
    /usr/lib/libQt6QuickWidgets.so* \
    /usr/lib/libQt6WebEngineWidgets.so* \
    /usr/lib/libQt6WebEngineCore.so*

find /usr/lib -name "libQt6WebEngineWidgets.so*"

mkdir -p "${APPDIR}/lib"

cp -av /usr/lib/libQt6WebEngineWidgets.so* \
    "${APPDIR}/lib/"

if [ ! -d "${APPDIR}" ]; then
    echo "Erro: AppDir não encontrado."
    exit 1
fi

echo
echo "==============================================================="
echo "Gerando AppImage"
echo "==============================================================="

quick-sharun --make-appimage

echo
echo "==============================================================="
echo "Arquivos gerados"
echo "==============================================================="

ls -lh "${OUTPATH}"

# Opcional:
# quick-sharun --test "${OUTPATH}"/*.AppImage