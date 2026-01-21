#!/usr/bin/env bash
rm *.deb -f
rm deb_build -Rf

VERSION=$(cat zapzap/__init__.py | grep '__version__' | awk '{print $3}' | sed "s/'//g")

mkdir -p deb_build/usr/local/bin deb_build/usr/share/zapzap deb_build/DEBIAN
mkdir -p deb_build/usr/share/applications
mkdir -p deb_build/usr/share/icons/hicolor/scalable/apps
mkdir -p deb_build/usr/share/metainfo

cat << 'EOF' > deb_build/usr/local/bin/zapzap
#!/usr/bin/env bash
cd /usr/share/zapzap
python3 -m zapzap
EOF

chmod +x deb_build/usr/local/bin/zapzap

cp share/applications/com.rtosta.zapzap.desktop deb_build/usr/share/applications/
cp share/icons/com.rtosta.zapzap.svg deb_build/usr/share/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg
cp share/metainfo/com.rtosta.zapzap.appdata.xml deb_build/usr/share/metainfo/

cat << EOF > deb_build/DEBIAN/control
Package: zapzap
Version: $VERSION
Section: utils
Priority: optional
Architecture: amd64
Depends: python3, python3-pyqt6.qtwebengine, python3-dbus
Maintainer: Katherine Flores <me@katherineflores.me>
Description: ZapZap - Cliente no oficial de WhatsApp Web para Linux.
EOF

rsync -av --exclude='deb_build' --exclude='*.deb' --exclude='.git' --exclude='.github' --exclude='make-deb.sh' --exclude='share' ./ deb_build/usr/share/zapzap/

dpkg-deb --build deb_build

mv deb_build.deb zapzap_${VERSION}_amd64.deb
