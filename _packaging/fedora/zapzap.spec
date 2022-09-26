# Maintained: Rafael Tosta <rafa.ecomp@gmail.com>
%global pkg_name zapzap
%global pkgname com.rtosta.zapzap

Name:           %{pkg_name}
Version:        4.4.1
Release:        0%{?dist}
Summary:        Whatsapp Desktop for linux
Group:          Applications/Communication/Whatsapp
License:        GPLv3+
URL:            https://github.com/rafatosta/zapzap

Source0:        https://github.com/rafatosta/%{pkg_name}/archive/%{version}.tar.gz

ExclusiveArch:	%{ix86} x86_64	

BuildRequires: python-build
BuildRequires: python-installer 
BuildRequires: python-setuptools
BuildRequires: python-wheel

Requires:       python-pyqt6
Requires:       python-pyqt6-webengine
Requires:       dbus-python

%description
    Whatsapp Desktop for Linux.

%prep

%build

%install

%files

%changelog
