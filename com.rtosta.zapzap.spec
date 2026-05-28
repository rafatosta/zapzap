# Fedora SPEC for ZapZap

%global srcname zapzap

Name:           %{srcname}
Version:        6.5
Release:        1%{?dist}
Summary:        WhatsApp Messenger for Linux

License:        GPL-3.0-only
URL:            https://github.com/rafatosta/zapzap

Source0:        %{url}/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-build
BuildRequires:  python3-installer
BuildRequires:  desktop-file-utils

Requires:       python3
Requires:       python3-dbus

%if 0%{?fedora}
Requires:       python3-pyqt6-base
Requires:       python3-pyqt6-sip
Requires:       python3-pyqt6-webengine
%endif

%description
ZapZap is a WhatsApp client for Linux built with Python and PyQt6.

%prep
%autosetup -n %{name}-%{version}

%build
%pyproject_wheel

%install
%pyproject_install

install -Dm644 \
    share/applications/com.rtosta.zapzap.desktop \
    %{buildroot}%{_datadir}/applications/com.rtosta.zapzap.desktop

install -Dm644 \
    share/icons/com.rtosta.zapzap.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg

%check

%files
%license LICENSE
%doc README.md

%{python3_sitelib}/zapzap
%{python3_sitelib}/zapzap-*.dist-info

%{_bindir}/zapzap

%{_datadir}/applications/com.rtosta.zapzap.desktop
%{_datadir}/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg