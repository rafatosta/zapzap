#!/bin/sh

set -eu

ARCH="$(uname -m)"
VERSION="$(cat ~/version)"

export ARCH
export OUTPATH="./dist"
export OUTNAME="ZapZap-${VERSION}-linux-${ARCH}.AppImage"

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

echo
echo "==============================================================="
echo "Criando AppDir"
echo "==============================================================="

# Falhe com um diagnóstico direto antes que o quick-sharun tente percorrer uma
# instalação Qt inconsistente. Isso também protege contra futuros desencontros
# de ABI em pacotes externos usados para reduzir o AppImage.
for QT_WEBENGINE_LIBRARY in \
    /usr/lib/libQt6WebEngineWidgets.so \
    /usr/lib/libQt6WebEngineCore.so
do
    MISSING_LIBRARIES="$(ldd "${QT_WEBENGINE_LIBRARY}" | sed -n '/not found/p')"

    if [ -n "${MISSING_LIBRARIES}" ]; then
        echo "Erro: ${QT_WEBENGINE_LIBRARY} possui dependências ausentes:" >&2
        echo "${MISSING_LIBRARIES}" >&2
        exit 1
    fi
done

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

APPDIR="./AppDir"

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
