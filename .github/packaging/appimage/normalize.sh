#!/usr/bin/env bash
set -euo pipefail

ARCH="${1:?usage: normalize.sh <arch>}"
VERSION="$(cat ~/version)"
APPIMAGE_NAME="ZapZap-${VERSION}-linux-${ARCH}.AppImage"

mkdir -p dist
appimage="$(find dist -maxdepth 1 -name "*.AppImage" -print -quit)"
if [[ -n "$appimage" ]]; then
  mv "$appimage" "dist/${APPIMAGE_NAME}"
fi

zsync="$(find dist -maxdepth 1 -name "*.zsync" -print -quit)"
if [[ -n "$zsync" ]]; then
  mv "$zsync" "dist/${APPIMAGE_NAME}.zsync"
fi

ls -lah dist/
