#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
VERSION="$(${ROOT_DIR}/.github/packaging/common/version.sh)"
DIST_DIR="${ROOT_DIR}/dist"
ARCH="$(rpm --eval '%{_arch}')"
FEDORA_RELEASE="$(rpm -E '%fedora')"

if [ -z "${FEDORA_RELEASE}" ] || [ "${FEDORA_RELEASE}" = "%fedora" ]; then
    FEDORA_RELEASE="unknown"
fi

RPM_SOURCE="$(find "${DIST_DIR}" -maxdepth 1 -type f -name 'zapzap-*.rpm' ! -name '*.src.rpm' | head -n 1 || true)"
SRPM_SOURCE="$(find "${DIST_DIR}" -maxdepth 1 -type f -name 'zapzap-*.src.rpm' | head -n 1 || true)"

if [ -z "${RPM_SOURCE}" ]; then
    echo "No binary RPM found in ${DIST_DIR}"
    exit 1
fi

RPM_TARGET="${DIST_DIR}/ZapZap-${VERSION}-fedora-${FEDORA_RELEASE}-${ARCH}.rpm"
mv -v "${RPM_SOURCE}" "${RPM_TARGET}"

if [ -n "${SRPM_SOURCE}" ]; then
    SRPM_TARGET="${DIST_DIR}/ZapZap-${VERSION}-fedora-${FEDORA_RELEASE}.src.rpm"
    mv -v "${SRPM_SOURCE}" "${SRPM_TARGET}"
fi

ls -lah "${DIST_DIR}"
