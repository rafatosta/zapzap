# Arquivo .spec para Fedora

%global srcname zapzap
%global srcversion  6.2

%global __python /usr/bin/python3
%global _rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.rpm

Name:           %{srcname}
Version:        %{srcversion}
Release:        1%{?dist}
Summary:        Zapzap - WhatsApp Messenger for Linux

License:        GNU General Public License v3.0
URL:            https://github.com/rafatosta/%{srcname}
Source0:        https://github.com/rafatosta/zapzap/archive/refs/tags/%{srcversion}.tar.gz


# Requisitos de construção
BuildArch:     noarch
BuildRequires:  python3-devel
BuildRequires:  desktop-file-utils
BuildRequires:  python3-setuptools

%if 0%{?fedora}
BuildRequires:   python3-pyqt6
Requires:   python3-pyqt6-base
Requires:   python3-pyqt6-sip
Requires:   python3-pyqt6-webengine
Requires:   python3-dbus
%endif

%if 0%{?mageia}
BuildRequires:  python3-qt6
Requires:   python3-pyqt6-sip
Requires:   python3-dbus
Requires:   python3-qt6-webenginewidgets
Requires:   python3-qt6
%endif


%description
Zapzap - WhatsApp Messenger for Linux

%prep
%autosetup -n %{srcname}-%{version}

%build
%py3_build

%install
%python3 setup.py install --root %{buildroot}
mkdir -p $RPM_BUILD_ROOT/usr/share/applications
mkdir -p $RPM_BUILD_ROOT/usr/share/icons/hicolor/scalable/apps/
cp -R share/applications/com.rtosta.zapzap.desktop $RPM_BUILD_ROOT/usr/share/applications/com.rtosta.zapzap.desktop
cp -R share/icons/com.rtosta.zapzap.svg $RPM_BUILD_ROOT/usr/share/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg


%check

%files
%license LICENSE
%doc README.md
%{python3_sitelib}/*

%{_bindir}/%{srcname}
/usr/share/applications/com.rtosta.zapzap.desktop
/usr/share/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg

