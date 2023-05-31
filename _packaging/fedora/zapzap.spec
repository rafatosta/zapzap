# Arquivo .spec para Fedora

%global srcname zapzap
%global srcversion  4.4.5

%global __python /usr/bin/python3
%global _rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.rpm

Name:           %{srcname}
Version:        %{srcversion}
Release:        1%{?dist}
Summary:        My Python App Test

License:        GNU General Public License v3.0
URL:            https://github.com/rafatosta/%{srcname}
Source0:        %{url}/archive/%{srcname}-%{version}.tar.gz


# Requisitos de construção
BuildArch:     noarch
BuildRequires: python3-pyqt6
BuildRequires: python3-pyqt6-webengine
BuildRequires: python3-dbus
BuildRequires: python3

%description
This is a test Python application.

%prep
%autosetup -n %{srcname}-%{version}

%build
%python3 setup.py build

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


%post
/sbin/ldconfig %{_libdir}

%postun
/sbin/ldconfig %{_libdir}

%changelog
* Thu May 30 2023 Your Name <yourname@example.com> - 0.1-1
- Initial package release
