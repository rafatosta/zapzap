#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

BUILD_INFO_PATH="zapzap/BuildInfo.py"
BUILD_INFO_BACKUP=""

if [[ -f "${BUILD_INFO_PATH}" ]]; then
  BUILD_INFO_BACKUP="$(mktemp)"
  cp "${BUILD_INFO_PATH}" "${BUILD_INFO_BACKUP}"
fi

cleanup_build_info() {
  if [[ -n "${BUILD_INFO_BACKUP}" && -f "${BUILD_INFO_BACKUP}" ]]; then
    cp "${BUILD_INFO_BACKUP}" "${BUILD_INFO_PATH}"
    rm -f "${BUILD_INFO_BACKUP}"
  else
    rm -f "${BUILD_INFO_PATH}"
  fi
}

trap cleanup_build_info EXIT

echo "Cleaning previous DEB build..."
rm -f ./*.deb
rm -rf deb_build

echo "Reading project version..."
VERSION="$(python3 - <<'PY'
import ast
from pathlib import Path

module = Path("zapzap/__init__.py")
tree = ast.parse(module.read_text(encoding="utf-8"), filename=str(module))

for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__version__":
                value = ast.literal_eval(node.value)
                print(value)
                raise SystemExit(0)

raise SystemExit("Could not find __version__ in zapzap/__init__.py")
PY
)"

echo "Version: ${VERSION}"

echo "Creating package structure..."
mkdir -p deb_build/DEBIAN
mkdir -p deb_build/usr/bin
mkdir -p deb_build/usr/share/zapzap
mkdir -p deb_build/usr/share/applications
mkdir -p deb_build/usr/share/icons/hicolor/scalable/apps
mkdir -p deb_build/usr/share/metainfo

echo "Creating launcher..."
cat << 'EOF' > deb_build/usr/bin/zapzap
#!/usr/bin/env bash
set -e

cd /usr/share/zapzap
exec python3 -m zapzap "$@"
EOF

chmod 0755 deb_build/usr/bin/zapzap

echo "Copying desktop integration files..."
install -Dm644 \
  share/applications/com.rtosta.zapzap.desktop \
  deb_build/usr/share/applications/com.rtosta.zapzap.desktop

install -Dm644 \
  share/icons/com.rtosta.zapzap.svg \
  deb_build/usr/share/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg

install -Dm644 \
  share/metainfo/com.rtosta.zapzap.appdata.xml \
  deb_build/usr/share/metainfo/com.rtosta.zapzap.appdata.xml

echo "Creating DEBIAN/control..."
cat << EOF > deb_build/DEBIAN/control
Package: zapzap
Version: ${VERSION}
Section: network
Priority: optional
Architecture: amd64
Depends: python3, python3-pyqt6.qtwebengine, python3-pyqt6.qtsvg, python3-dbus, qt6-wayland, qt6-qpa-plugins
Maintainer: Rafael Tosta <rafa.ecomp@gmail.com>
Description: ZapZap - WhatsApp Messenger for Linux.
 An unofficial WhatsApp desktop application written in Python and PyQt6.
EOF

echo "Copying application files..."
rsync -a \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  --exclude='.github' \
  --exclude='dist' \
  --exclude='build' \
  --exclude='deb_build' \
  zapzap \
  LICENSE \
  README.md \
  requirements.txt \
  pyproject.toml \
  deb_build/usr/share/zapzap/

echo "Building DEB package..."
dpkg-deb --root-owner-group --build deb_build

OUTPUT="zapzap-${VERSION}-amd64.deb"

mv deb_build.deb "${OUTPUT}"

echo
echo "DEB package created successfully:"
ls -lh "${OUTPUT}"