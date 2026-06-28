Name:           zapzap
Version:        %{?_version}%{!?_version:0}
Release:        1%{?dist}
Summary:        WhatsApp desktop client for Linux

License:        GPL-3.0-or-later
URL:            https://rtosta.com/zapzap
Source0:        %{name}-%{version}.tar.gz


BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-pyqt6
BuildRequires:  python3-pyqt6-webengine
BuildRequires:  python3-dbus
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel

Requires:       python3
Requires:       python3-pyqt6
Requires:       python3-pyqt6-webengine
Requires:       python3-dbus

%description
ZapZap is an unofficial WhatsApp Web desktop client for Linux,
written in Python with PyQt6 and QtWebEngine.

%prep
%autosetup -n %{name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files zapzap

# Some project layouts already install desktop/metainfo/icon files through the
# Python wheel. These fallbacks keep the RPM compatible with both layouts.
if [ ! -f "%{buildroot}%{_datadir}/applications/com.rtosta.zapzap.desktop" ]; then
    for file in \
        "com.rtosta.zapzap.desktop" \
        "data/com.rtosta.zapzap.desktop" \
        "share/applications/com.rtosta.zapzap.desktop" \
        "zapzap/com.rtosta.zapzap.desktop"; do
        if [ -f "$file" ]; then
            install -Dm0644 "$file" "%{buildroot}%{_datadir}/applications/com.rtosta.zapzap.desktop"
            break
        fi
    done
fi

if [ ! -f "%{buildroot}%{_datadir}/metainfo/com.rtosta.zapzap.appdata.xml" ]; then
    for file in \
        "com.rtosta.zapzap.appdata.xml" \
        "data/com.rtosta.zapzap.appdata.xml" \
        "share/metainfo/com.rtosta.zapzap.appdata.xml" \
        "zapzap/com.rtosta.zapzap.appdata.xml"; do
        if [ -f "$file" ]; then
            install -Dm0644 "$file" "%{buildroot}%{_datadir}/metainfo/com.rtosta.zapzap.appdata.xml"
            break
        fi
    done
fi

if [ ! -f "%{buildroot}%{_datadir}/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg" ]; then
    for file in \
        "com.rtosta.zapzap.svg" \
        "data/com.rtosta.zapzap.svg" \
        "share/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg" \
        "zapzap/com.rtosta.zapzap.svg"; do
        if [ -f "$file" ]; then
            install -Dm0644 "$file" "%{buildroot}%{_datadir}/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg"
            break
        fi
    done
fi

%check
if [ -f "%{buildroot}%{_datadir}/applications/com.rtosta.zapzap.desktop" ]; then
    desktop-file-validate "%{buildroot}%{_datadir}/applications/com.rtosta.zapzap.desktop"
fi

if [ -f "%{buildroot}%{_datadir}/metainfo/com.rtosta.zapzap.appdata.xml" ]; then
    appstream-util validate-relax --nonet "%{buildroot}%{_datadir}/metainfo/com.rtosta.zapzap.appdata.xml"
fi

%files -f %{pyproject_files}
%license LICENSE*
%doc README*
%{_bindir}/zapzap
%{_datadir}/applications/com.rtosta.zapzap.desktop
%{_datadir}/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg
%{_datadir}/metainfo/com.rtosta.zapzap.appdata.xml

%changelog
* Sun Jun 28 2026 Rafael Tosta <rafa.ecomp@gmail.com> - %{version}-1
- Build RPM package with native Fedora PyQt6 and QtWebEngine dependencies
