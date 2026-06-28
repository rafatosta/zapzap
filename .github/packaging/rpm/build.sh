#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
VERSION="$(${ROOT_DIR}/.github/packaging/common/version.sh)"
RPMBUILD_DIR="${ROOT_DIR}/rpmbuild"
SOURCE_NAME="zapzap-${VERSION}.tar.gz"
SPEC_SOURCE="${ROOT_DIR}/.github/packaging/rpm/zapzap.spec"
SPEC_TARGET="${RPMBUILD_DIR}/SPECS/zapzap.spec"

log() {
    echo
    echo "==============================================================="
    echo "$1"
    echo "==============================================================="
}

log "Preparing RPM build tree"
rm -rf "${RPMBUILD_DIR}" "${ROOT_DIR}/dist"
mkdir -p \
    "${RPMBUILD_DIR}/BUILD" \
    "${RPMBUILD_DIR}/BUILDROOT" \
    "${RPMBUILD_DIR}/RPMS" \
    "${RPMBUILD_DIR}/SOURCES" \
    "${RPMBUILD_DIR}/SPECS" \
    "${RPMBUILD_DIR}/SRPMS" \
    "${ROOT_DIR}/dist"

log "Creating source archive"
git -C "${ROOT_DIR}" archive \
    --format=tar.gz \
    --prefix="zapzap-${VERSION}/" \
    HEAD \
    -o "${RPMBUILD_DIR}/SOURCES/${SOURCE_NAME}"

log "Copying RPM spec"
cp "${SPEC_SOURCE}" "${SPEC_TARGET}"

log "Building RPM"
rpmbuild \
    --define "_topdir ${RPMBUILD_DIR}" \
    --define "_version ${VERSION}" \
    -ba "${SPEC_TARGET}"

log "Collecting RPM artifacts"
find "${RPMBUILD_DIR}/RPMS" "${RPMBUILD_DIR}/SRPMS" -type f -name "*.rpm" -exec cp -v {} "${ROOT_DIR}/dist/" \;
ls -lah "${ROOT_DIR}/dist/"
