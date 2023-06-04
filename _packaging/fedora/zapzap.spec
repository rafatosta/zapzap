# Arquivo .spec para Fedora

%global srcname zapzap
%global tag_version  4.4.6

%global __python /usr/bin/python3
%global _rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.rpm

Name:           %{srcname}
Version:        %{tag_version}
Release:        2%{?dist}
Summary:        WhatsApp desktop application written in Pyqt6 + PyQt6-WebEngine.

License:        GNU General Public License v3.0
URL:            https://github.com/rafatosta/%{srcname}
Source0:        https://github.com/rafatosta/zapzap/archive/refs/tags/%{tag_version}.tar.gz


# Requisitos de construção
BuildArch:     noarch
BuildRequires:  python3-devel
BuildRequires:  desktop-file-utils
BuildRequires:  python3-setuptools

BuildRequires:   python3-pyqt6
Requires:   python3-pyqt6-base
Requires:   python3-pyqt6-sip
Requires:   python3-pyqt6-webengine
Requires:   python3-dbus

%description
WhatsApp desktop application written in Pyqt6 + PyQt6-WebEngine.
    Features come with Whatsapp web
    Icon in systray changes if there are new messages
    Customizable Systray icons
    System style (light and dark)
    Fullscreen mode
    Background running
    Spellchecker
    Drag and drop
    Work area notifications
    Personalized window decoration
    Shortcuts for the main options

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
/usr/lib/python3.11/site-packages/*
%{_bindir}/%{srcname}
/usr/share/applications/com.rtosta.zapzap.desktop
/usr/share/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg

%changelog
* Wed May 31 2023 Rafael Tosta <rafa.ecomp@gmail.com> - 4.4.6-2
- 1.0
- Initial package release
