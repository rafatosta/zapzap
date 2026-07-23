#!/usr/bin/env bash
set -euo pipefail

echo "# === macOS Builder ==="

APP_NAME="ZapZap"
VERSION=$(python3 -c "import sys, os; sys.path.insert(0, os.getcwd()); import zapzap; print(zapzap.__version__)")
if [ -z "$VERSION" ]; then
    VERSION="dev"
fi

echo "# === Installing dependencies ==="
python -m pip install --upgrade pip
python -m pip install pyinstaller
python -m pip install -r requirements.txt

echo "# === Cleaning previous builds ==="
rm -rf dist build

echo "# === Running PyInstaller ==="
python -m PyInstaller \
    --name "$APP_NAME" \
    --windowed \
    --noconfirm \
    --add-data "zapzap/po:zapzap/po" \
    --add-data "zapzap/assets:zapzap/assets" \
    --add-data "zapzap/features/browser/web/scripts:zapzap/features/browser/web/scripts" \
    zapzap/__main__.py

echo "# === Packaging into DMG ==="
DMG_NAME="${APP_NAME}-${VERSION}-macos-universal.dmg"
# Create DMG using hdiutil
if [ -d "dist/${APP_NAME}.app" ]; then
    hdiutil create -volname "$APP_NAME" -srcfolder "dist/${APP_NAME}.app" -ov -format UDZO "dist/$DMG_NAME"
    echo "Build generated at dist/$DMG_NAME"
else
    echo "Error: Application bundle dist/${APP_NAME}.app not found."
    exit 1
fi
