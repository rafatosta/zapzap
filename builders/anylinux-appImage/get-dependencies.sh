#!/bin/sh

set -eu

ARCH=$(uname -m)

echo "Installing package dependencies..."
echo "---------------------------------------------------------------"
pacman -Syu --noconfirm    \
    kvantum        \
    lxqt-qtplugin  \
    pipewire-audio \
    pipewire-jack  \
    python         \
    qt6ct

echo "Installing debloated packages..."
echo "---------------------------------------------------------------"
get-debloated-pkgs --add-common --prefer-nano ffmpeg-mini

# Comment this out if you need an AUR package
if [ "${DEVEL_RELEASE-}" = 1 ]; then
    package=zapzap-git
else
    package=zapzap
fi
make-aur-package "$package"
pacman -Q "$package" | awk '{print $2; exit}' > ~/version

# If the application needs to be manually built that has to be done down here
