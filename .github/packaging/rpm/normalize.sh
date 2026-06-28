#!/usr/bin/env bash

set -euo pipefail

ARCH="${1:-}"

if [[ -z "${ARCH}" ]]; then
    echo "Architecture argument is required."
    exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
DIST_DIR="${ROOT_DIR}/dist"

log() {
    echo
    echo "==============================================================="
    echo "$1"
    echo "==============================================================="
}

read_version() {
    python3 - <<'PY'
import re
from pathlib import Path

init_file = Path("zapzap/__init__.py")

if not init_file.exists():
    raise SystemExit("zapzap/__init__.py not found")

text = init_file.read_text(encoding="utf-8")

match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", text)

if not match:
    raise SystemExit("Could not find __version__ in zapzap/__init__.py")

print(match.group(1))
PY
}

cd "${ROOT_DIR}"

log "Reading project version"

VERSION="$(read_version)"
echo "Version: ${VERSION}"
echo "Arch: ${ARCH}"

log "Normalizing RPM artifacts"

MAIN_RPM="$(
    find "${DIST_DIR}" \
    -maxdepth 1 \
    -type f \
    -name "zapzap-${VERSION}-*.${ARCH}.rpm" \
    ! -name "*.src.rpm" \
    | head -n 1
)"

if [[ -z "${MAIN_RPM}" ]]; then
    echo "No RPM artifact found for architecture: ${ARCH}"
    echo
    echo "Available files in ${DIST_DIR}:"
    find "${DIST_DIR}" -maxdepth 1 -type f -print || true
    exit 1
fi

FINAL_NAME="ZapZap-${VERSION}-fedora-44-${ARCH}.rpm"
FINAL_PATH="${DIST_DIR}/${FINAL_NAME}"

cp -f "${MAIN_RPM}" "${FINAL_PATH}"

log "Normalized RPM"

ls -lah "${FINAL_PATH}"