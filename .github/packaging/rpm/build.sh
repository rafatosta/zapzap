#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RPMBUILD_DIR="${ROOT_DIR}/rpmbuild"
SOURCES_DIR="${RPMBUILD_DIR}/SOURCES"
SPECS_DIR="${RPMBUILD_DIR}/SPECS"
DIST_DIR="${ROOT_DIR}/dist"

SPEC_SOURCE="${ROOT_DIR}/.github/packaging/rpm/zapzap.spec"
SPEC_TARGET="${SPECS_DIR}/zapzap.spec"

BUILD_MODE="rpm"

usage() {
    cat <<'USAGE'
Usage: .github/packaging/rpm/build.sh [--rpm|--srpm|--all]

Options:
  --rpm   Build binary RPM packages only. Default.
  --srpm  Build source RPM only, suitable for Copr submission.
  --all   Build binary RPM packages and source RPM.
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --rpm)
            BUILD_MODE="rpm"
            shift
            ;;
        --srpm)
            BUILD_MODE="srpm"
            shift
            ;;
        --all)
            BUILD_MODE="all"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

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

copy_artifacts() {
    local source_dir="$1"
    local pattern="$2"

    find "${source_dir}" \
        -type f \
        -name "${pattern}" \
        -exec cp -v {} "${DIST_DIR}/" \;
}

log "Configuring Git safe directory"

git config --global --add safe.directory "${ROOT_DIR}"

cd "${ROOT_DIR}"

log "Reading project version"

VERSION="$(read_version)"
SOURCE_NAME="zapzap-${VERSION}.tar.gz"

echo "Version: ${VERSION}"
echo "Build mode: ${BUILD_MODE}"

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

log "Validating BuildInfo.py"

if [[ ! -f "${ROOT_DIR}/zapzap/BuildInfo.py" ]]; then
    echo "zapzap/BuildInfo.py was not created."
    echo "Run .github/packaging/common/build-info.sh before building the RPM."
    exit 1
fi

cat "${ROOT_DIR}/zapzap/BuildInfo.py"

log "Creating source archive"

TMP_SOURCE_DIR="$(mktemp -d)"
SOURCE_ROOT="${TMP_SOURCE_DIR}/zapzap-${VERSION}"

mkdir -p "${SOURCE_ROOT}"

rsync -a \
    --exclude ".git" \
    --exclude ".github" \
    --exclude "rpmbuild" \
    --exclude "dist" \
    --exclude ".venv" \
    --exclude "venv" \
    --exclude "__pycache__" \
    --exclude "*.pyc" \
    "${ROOT_DIR}/" \
    "${SOURCE_ROOT}/"

tar -C "${TMP_SOURCE_DIR}" \
    -czf "${SOURCES_DIR}/${SOURCE_NAME}" \
    "zapzap-${VERSION}"

rm -rf "${TMP_SOURCE_DIR}"

log "Copying RPM spec"

cp "${SPEC_SOURCE}" "${SPEC_TARGET}"

# The GitHub build defines _version while creating the first SRPM, but Copr
# imports the SRPM into dist-git and rebuilds it without that custom macro.
# Therefore the spec stored inside the SRPM must contain the concrete Version.
sed -i "s/^Version:.*/Version:        ${VERSION}/" "${SPEC_TARGET}"

echo "RPM spec version after normalization:"
grep -E "^(Name|Version|Release|Source0):" "${SPEC_TARGET}"

case "${BUILD_MODE}" in
    rpm)
        log "Building binary RPM"
        rpmbuild \
            --define "_topdir ${RPMBUILD_DIR}" \
            --define "_version ${VERSION}" \
            -bb "${SPEC_TARGET}"

        log "Collecting RPM artifacts"
        copy_artifacts "${RPMBUILD_DIR}/RPMS" "*.rpm"
        ;;

    srpm)
        log "Building source RPM"
        rpmbuild \
            --define "_topdir ${RPMBUILD_DIR}" \
            --define "_version ${VERSION}" \
            -bs "${SPEC_TARGET}"

        log "Collecting SRPM artifacts"
        copy_artifacts "${RPMBUILD_DIR}/SRPMS" "*.src.rpm"
        ;;

    all)
        log "Building binary RPM and source RPM"
        rpmbuild \
            --define "_topdir ${RPMBUILD_DIR}" \
            --define "_version ${VERSION}" \
            -ba "${SPEC_TARGET}"

        log "Collecting RPM and SRPM artifacts"
        copy_artifacts "${RPMBUILD_DIR}/RPMS" "*.rpm"
        copy_artifacts "${RPMBUILD_DIR}/SRPMS" "*.src.rpm"
        ;;

    *)
        echo "Invalid build mode: ${BUILD_MODE}"
        exit 1
        ;;
esac

log "Generated artifacts"

ls -lah "${DIST_DIR}"
