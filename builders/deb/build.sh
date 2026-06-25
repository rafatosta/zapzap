#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "${SCRIPT_DIR}/../.." && pwd)

. "${ROOT_DIR}/builders/common/common.sh"

PACKAGE_NAME=${PACKAGE_NAME:-zapzap}
VERSION=$(project_version)
ARCH=${ARCH:-$(dpkg --print-architecture)}
BUILD_DIR=${BUILD_DIR:-"${ROOT_DIR}/.packaging/deb"}
PACKAGE_ROOT="${BUILD_DIR}/${PACKAGE_NAME}_${VERSION}_${ARCH}"

rm -rf "${PACKAGE_ROOT}"
mkdir -p "${PACKAGE_ROOT}/DEBIAN" "${DIST_DIR}"

export DESTDIR="${PACKAGE_ROOT}"
export PREFIX="${PREFIX:-/usr}"

prepare_package

cat > "${PACKAGE_ROOT}/DEBIAN/control" <<CONTROL
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: net
Priority: optional
Architecture: ${ARCH}
Maintainer: Rafael Tosta <rafa.ecomp@gmail.com>
Depends: python3, python3-pyqt6, python3-pyqt6.qtwebengine
Description: WhatsApp desktop client web app
 ZapZap is a WhatsApp desktop client web app.
CONTROL

log "Building DEB package"
dpkg-deb --build "${PACKAGE_ROOT}" "${DIST_DIR}/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
