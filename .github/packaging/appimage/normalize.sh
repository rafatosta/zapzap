#!/usr/bin/env bash
set -euo pipefail

ARCH="${1:?usage: normalize.sh <arch>}"
VERSION="$(cat ~/version)"
APPIMAGE_NAME="ZapZap-${VERSION}-linux-${ARCH}.AppImage"
APPIMAGE_PATH="dist/${APPIMAGE_NAME}"
ZSYNC_PATH="${APPIMAGE_PATH}.zsync"

mkdir -p dist
mapfile -t appimages < <(find dist -maxdepth 1 -name "*.AppImage" -print)
mapfile -t zsync_files < <(find dist -maxdepth 1 -name "*.zsync" -print)

if (( ${#appimages[@]} != 1 )); then
  echo "Expected exactly one AppImage in dist, found ${#appimages[@]}." >&2
  exit 1
fi

if (( ${#zsync_files[@]} != 1 )); then
  echo "Expected exactly one zsync control file in dist, found ${#zsync_files[@]}." >&2
  exit 1
fi

if [[ "${appimages[0]}" != "${APPIMAGE_PATH}" ]]; then
  mv -- "${appimages[0]}" "${APPIMAGE_PATH}"
fi

rm -- "${zsync_files[0]}"
zsyncmake \
  -e \
  -f "${APPIMAGE_NAME}" \
  -u "${APPIMAGE_NAME}" \
  -o "${ZSYNC_PATH}" \
  "${APPIMAGE_PATH}"

zsync_filename="$(
  LC_ALL=C sed -n 's/^Filename: //p; /^$/q' "${ZSYNC_PATH}"
)"
zsync_url="$(
  LC_ALL=C sed -n 's/^URL: //p; /^$/q' "${ZSYNC_PATH}"
)"

if [[ "${zsync_filename}" != "${APPIMAGE_NAME}" ]]; then
  echo "Invalid zsync Filename: ${zsync_filename}" >&2
  exit 1
fi

if [[ "${zsync_url}" != "${APPIMAGE_NAME}" ]]; then
  echo "Invalid zsync URL: ${zsync_url}" >&2
  exit 1
fi

ls -lah dist/
