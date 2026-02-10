# Arquivo .spec para Fedora (pyproject.toml)

%global srcname zapzap
%global srcversion 6.2.10.1

Name:           %{srcname}
Version:        %{srcversion}
Release:        1%{?dist}
Summary:        Zapzap - WhatsApp Messenger for Linux

License:        GPL-3.0-or-later
URL:            https://github.com/rafatosta/%{srcname}
Source0:        https://github.com/rafatosta/zapzap/archive/refs/tags/%{srcversion}.tar.gz

BuildArch:      noarch

# Requisitos de build (PEP 517)
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-build
BuildRequires:  pyproject-rpm-macros
BuildRequires:  desktop-file-utils

%if 0%{?fedora}
BuildRequires:  python3-pyqt6
Requires:       python3-pyqt6-base
Requires:       python3-pyqt6-sip
Requires:       python3-pyqt6-webengine
Requires:       python3-dbus
%endif

%if 0%{?mageia}
BuildRequires:  python3-qt6
Requires:       python3-pyqt6-sip
Requires:       python3-dbus
Requires:       python3-qt6-webenginewidgets
Requires:       python3-qt6
%endif

%description
Zapzap is an unofficial WhatsApp desktop client for Linux, built with Python and Qt.

%prep
%autosetup -n %{srcname}-%{version}

%build
%pyproject_build

%install
%pyproject_install

# Arquivos desktop e ícone
install -Dm644 share/applications/com.rtosta.zapzap.desktop \
    %{buildroot}%{_datadir}/applications/com.rtosta.zapzap.desktop

install -Dm644 share/icons/com.rtosta.zapzap.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg

%check
# Testes opcionais (se existirem)
# %pytest

%files
%license LICENSE
%doc README.md

%{python3_sitelib}/zapzap*
%{_bindir}/zapzap
%{_datadir}/applications/com.rtosta.zapzap.desktop
%{_datadir}/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg
