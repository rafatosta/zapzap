%global srcname zapzap
%global srcversion 6.2.1

%global _rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.rpm

Name:           %{srcname}
Version:        %{srcversion}
Release:        1%{?dist}
Summary:        Zapzap - WhatsApp Messenger for Linux

License:        GPL-3.0-or-later
URL:            https://github.com/rafatosta/%{srcname}
Source0:        https://github.com/rafatosta/zapzap/archive/refs/tags/%{srcversion}.tar.gz

BuildArch:      noarch

# Requisitos de build
BuildRequires:  python3-devel
BuildRequires:  python3-pyproject-macros
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
Zapzap - WhatsApp Messenger for Linux


%prep
%autosetup -n %{srcname}-%{version}


%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files %{srcname}


%check
# se tiver testes, chamar pytest ou similar aqui


%files -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/%{srcname}
%{_datadir}/applications/com.rtosta.zapzap.desktop
%{_datadir}/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg