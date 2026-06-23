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

echo
echo "==============================================================="
echo "Verificando dicionários instalados"
echo "==============================================================="

DICT_SRC="$(python - <<'EOF'
from importlib.resources import files

path = files("zapzap") / "qtwebengine_dictionaries"

print(path)
EOF
)"

echo "Origem: ${DICT_SRC}"

find "${DICT_SRC}" -name "*.bdic" | sort

echo
echo "==============================================================="
echo "Criando AppDir"
echo "==============================================================="

quick-sharun \
    "${ZAPZAP_BIN}" \
    /usr/lib/libQt6Network.so* \
    /usr/lib/libQt6Widgets.so* \
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
echo "Copiando dicionários para o AppDir"
echo "==============================================================="

DICT_DST="${APPDIR}/qtwebengine_dictionaries"

mkdir -p "${DICT_DST}"

cp -av \
    "${DICT_SRC}"/*.bdic \
    "${DICT_DST}/"

echo
echo "Dicionários no AppDir:"
find "${APPDIR}" -name "*.bdic" | sort

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