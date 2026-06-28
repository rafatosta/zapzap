#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RPMBUILD_DIR="${ROOT_DIR}/rpmbuild"
SOURCES_DIR="${RPMBUILD_DIR}/SOURCES"
SPECS_DIR="${RPMBUILD_DIR}/SPECS"
DIST_DIR="${ROOT_DIR}/dist"

SPEC_SOURCE="${ROOT_DIR}/.github/packaging/rpm/zapzap.spec"
SPEC_TARGET="${SPECS_DIR}/zapzap.spec"

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

log "Configuring Git safe directory"

git config --global --add safe.directory "${ROOT_DIR}"

cd "${ROOT_DIR}"

log "Reading project version"

VERSION="$(read_version)"
SOURCE_NAME="zapzap-${VERSION}.tar.gz"

echo "Version: ${VERSION}"

log "Preparing RPM build tree"

rm -rf "${RPMBUILD_DIR}" "${DIST_DIR}"

mkdir -p \
    "${RPMBUILD_DIR}/BUILD" \
    "${RPMBUILD_DIR}/BUILDROOT" \
    "${RPMBUILD_DIR}/RPMS" \
    "${RPMBUILD_DIR}/SOURCES" \
    "${RPMBUILD_DIR}/SPECS" \
    "${RPMBUILD_DIR}/SRPMS" \
    "${DIST_DIR}"

log "Creating source archive"

git -C "${ROOT_DIR}" archive \
    --format=tar.gz \
    --prefix="zapzap-${VERSION}/" \
    HEAD \
    -o "${SOURCES_DIR}/${SOURCE_NAME}"

log "Copying RPM spec"

cp "${SPEC_SOURCE}" "${SPEC_TARGET}"

log "Building RPM"

rpmbuild \
    --define "_topdir ${RPMBUILD_DIR}" \
    --define "_version ${VERSION}" \
    -ba "${SPEC_TARGET}"

log "Collecting RPM artifacts"

find "${RPMBUILD_DIR}/RPMS" "${RPMBUILD_DIR}/SRPMS" \
    -type f \
    -name "*.rpm" \
    -exec cp -v {} "${DIST_DIR}/" \;

ls -lah "${DIST_DIR}"