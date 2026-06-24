#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "${SCRIPT_DIR}/../.." && pwd)

. "${ROOT_DIR}/builders/common/common.sh"

log "Installing package dependencies"
pacman -Syu --noconfirm \
    base-devel \
    ffmpeg \
    git \
    kvantum \
    lxqt-qtplugin \
    pipewire-audio \
    pipewire-jack \
    python \
    python-build \
    python-installer \
    python-pip \
    python-setuptools \
    python-wheel \
    qt6-base \
    qt6-webengine \
    qt6ct \
    python-pyqt6 \
    python-pyqt6-webengine

log "Installing debloated packages"
get-debloated-pkgs --add-common --prefer-nano ffmpeg-mini

log "Downloading dictionaries"
if [ ! -d "${ROOT_DIR}/qtwebengine_dictionaries" ]; then
    git clone \
      --depth=1 \
      https://github.com/rafatosta/qtwebengine_dictionaries.git \
      "${ROOT_DIR}/qtwebengine_dictionaries"
fi

export DESTDIR="${DESTDIR:-${ROOT_DIR}/AppDir}"
export PREFIX="${PREFIX:-/usr}"

prepare_package

log "Saving version"
project_version > "${HOME}/version"

log "Done"
