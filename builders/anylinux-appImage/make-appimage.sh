#!/bin/sh

set -eu

ARCH=$(uname -m)
export ARCH
export OUTPATH=./dist
export ADD_HOOKS="self-updater.hook:wayland-is-broken.hook"
export UPINFO="gh-releases-zsync|${GITHUB_REPOSITORY%/*}|${GITHUB_REPOSITORY#*/}|latest|*$ARCH.AppImage.zsync"
export ICON=/usr/share/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg
export DESKTOP=/usr/share/applications/com.rtosta.zapzap.desktop
export DEPLOY_OPENGL=1
export DEPLOY_VULKAN=1
export DEPLOY_PIPEWIRE=1
export DEPLOY_PYTHON=1
export DEPLOY_QT=1
export QT_DIR=qt6
export DEPLOY_QT_WEB_ENGINE=1

# Deploy dependencies
quick-sharun /usr/bin/zapzap /usr/lib/libQt6Network.so*
#   /usr/lib/libQt6Core.so*   \
#   /usr/lib/libQt6Gui.so*    \

# Additional changes can be done in between here

# Turn AppDir into AppImage
quick-sharun --make-appimage

# Test the app for 12 seconds, if the app normally quits before that time
# then skip this or check if some flag can be passed that makes it stay open
quick-sharun --test ./dist/*.AppImage
