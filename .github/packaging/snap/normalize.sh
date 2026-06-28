#!/usr/bin/env bash
set -euo pipefail

SNAP_PATH="${1:?usage: normalize.sh <snap-path>}"
VERSION="$(.github/packaging/common/version.sh)"
ARCH="$(dpkg --print-architecture)"
SNAP_NAME="ZapZap-${VERSION}-linux-${ARCH}.snap"
mkdir -p dist
cp "$SNAP_PATH" "dist/${SNAP_NAME}"
echo "dist/${SNAP_NAME}"
