Name:           zapzap
Version:        %{?_version}%{!?_version:0}
Release:        1%{?dist}
Summary:        WhatsApp desktop client for Linux

License:        GPL-3.0-or-later
URL:            https://rtosta.com/zapzap
Source0:        %{name}-%{version}.tar.gz

%global debug_package %{nil}

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  pyproject-rpm-macros

BuildRequires:  python3-pyqt6
BuildRequires:  python3-pyqt6-webengine
BuildRequires:  python3-dbus

BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

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

install -Dm0644 share/applications/com.rtosta.zapzap.desktop \
    %{buildroot}%{_datadir}/applications/com.rtosta.zapzap.desktop

install -Dm0644 share/icons/com.rtosta.zapzap.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg

install -Dm0644 share/metainfo/com.rtosta.zapzap.appdata.xml \
    %{buildroot}%{_datadir}/metainfo/com.rtosta.zapzap.appdata.xml

%check
desktop-file-validate \
    %{buildroot}%{_datadir}/applications/com.rtosta.zapzap.desktop

appstream-util validate-relax --nonet \
    %{buildroot}%{_datadir}/metainfo/com.rtosta.zapzap.appdata.xml

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