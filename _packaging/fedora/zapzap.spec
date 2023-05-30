# Arquivo .spec para Fedora

%global srcname zapzap
%global srcversion 4.4.5

%global __python /usr/bin/python3
%global _rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm

Name:           %{srcname}
Version:        %{srcversion}
Release:        1%{?dist}
Summary:        My Python App Test

License:        GNU General Public License v3.0
URL:            https://github.com/rafatosta/%{srcname}
Source0:        %{url}/archive/%{srcname}-%{version}.tar.gz

# Requisitos de construção
BuildArch:      noarch
BuildRequires:  python3-setuptools

# Requisitos de execução
Requires: python3-pyqt6
Requires: python3-pyqt6-webengine
Requires: python3-dbus
Requires: python3

%description
This is a test Python application.

%prep
%autosetup -n %{srcname}-%{version}

%build
%python3 setup.py build

%install
%python3 setup.py install --root %{buildroot}

%check
%{__python3} setup.py test   

%files
%license LICENSE
%doc README.md
%{_bindir}/%{srcname}
/usr/lib/python3.11/site-packages/*

%post
/sbin/ldconfig %{_libdir}

%postun
/sbin/ldconfig %{_libdir}

%changelog
* Thu May 30 2023 Your Name <yourname@example.com> - 0.1-1
- Initial package release
