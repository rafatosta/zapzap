#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/../../.."

echo "# === macOS Builder ==="

APP_NAME="ZapZap"

echo "# === Installing dependencies ==="
python -m pip install --upgrade pip
python -m pip install pyinstaller
python -m pip install -r requirements.txt

VERSION=$(bash .github/packaging/common/version.sh)
if [ -z "$VERSION" ]; then
    VERSION="dev"
fi

echo "# === Cleaning previous builds ==="
rm -rf dist build

echo "# === Compiling native notification bridge ==="
bash .github/packaging/macos/build-native.sh

echo "# === Running PyInstaller ==="
python -m PyInstaller \
    --noconfirm \
    --collect-submodules zapzap.features.settings.pages \
    .github/packaging/macos/ZapZap.spec

echo "# === Packaging into DMG ==="
ARCH=$(uname -m)
DMG_NAME="${APP_NAME}-${VERSION}-macos-${ARCH}.dmg"
# Create DMG using hdiutil
if [ -d "dist/${APP_NAME}.app" ]; then
    hdiutil create -volname "$APP_NAME" -srcfolder "dist/${APP_NAME}.app" -ov -format UDZO "dist/$DMG_NAME"
    echo "Build generated at dist/$DMG_NAME"
else
    echo "Error: Application bundle dist/${APP_NAME}.app not found."
    exit 1
fi
