#!/usr/bin/env bash

set -euo pipefail

ARCH="${1:-}"

if [[ -z "$ARCH" ]]; then
    echo "Architecture argument is required."
    exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
DIST_DIR="${ROOT_DIR}/dist-rpm"

mkdir -p "${DIST_DIR}"

VERSION="$(
python3 - <<'PY'
import re
from pathlib import Path

text = Path("zapzap/__init__.py").read_text()
match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", text)

if not match:
    raise SystemExit("Could not find __version__")

print(match.group(1))
PY
)"

RPM_FILE="$(find "${HOME}/rpmbuild/RPMS" -type f -name "*.rpm" | head -n 1)"

if [[ -z "${RPM_FILE}" ]]; then
    echo "No RPM file found."
    exit 1
fi

FINAL_NAME="ZapZap-${VERSION}-fedora-44-${ARCH}.rpm"

cp "${RPM_FILE}" "${DIST_DIR}/${FINAL_NAME}"

echo "RPM normalized:"
echo "${DIST_DIR}/${FINAL_NAME}"