#!/bin/sh

set -eu

echo "Installing package dependencies..."
echo "---------------------------------------------------------------"

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


echo "Installing debloated packages..."
echo "---------------------------------------------------------------"

get-debloated-pkgs --add-common --prefer-nano ffmpeg-mini

echo "Downloading dictionaries..."
git clone \
  --depth=1 \
  https://github.com/rafatosta/qtwebengine_dictionaries.git

mkdir -p zapzap/qtwebengine_dictionaries

cp \
  qtwebengine_dictionaries/*.bdic \
  zapzap/qtwebengine_dictionaries/

echo "Building ZapZap..."
echo "---------------------------------------------------------------"

python -m build

echo "Installing ZapZap..."
echo "---------------------------------------------------------------"

python -m installer dist/*.whl

echo "Checking installation..."
echo "---------------------------------------------------------------"

which zapzap

zapzap --help >/dev/null 2>&1 || true

echo "Saving version..."
echo "---------------------------------------------------------------"

python - <<'EOF' > ~/version
from pathlib import Path

wheel = next(Path("dist").glob("zapzap-*.whl"))

version = wheel.name.split("-")[1]

print(version)
EOF

echo "Done."