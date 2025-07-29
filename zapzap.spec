Name:           zapzap
Version:        1.0.0
Release:        1%{?dist}
Summary:        Zapzap Electron app

License:        MIT
URL:            https://github.com/seu-usuario/zapzap
Source0:        %{name}-%{version}.tar.gz

BuildArch:      x86_64
BuildRoot:      %{_tmppath}/%{name}-%{version}-buildroot

Requires:       libX11, libXcomposite, libXcursor, libXdamage, libXext, libXi, libXtst, \
                libnss3, libasound2, libatk1.0, libgtk-3, libxss1, libxrandr, libcups

%description
Zapzap is an Electron app for ...

%prep
# Preparar a fonte
# Se você usar um tarball, extrai aqui
# Caso build seja via prebuild, pode deixar vazio

%build
# Normalmente vazio para app Electron pré-construído

%install
# Copia os arquivos para o diretório correto do sistema
mkdir -p %{buildroot}/usr/share/%{name}
cp -r * %{buildroot}/usr/share/%{name}/

# Pode criar um link simbólico para o executável na bin
mkdir -p %{buildroot}/usr/bin
ln -s /usr/share/%{name}/zapzap %{buildroot}/usr/bin/zapzap

%files
%defattr(-,root,root,-)
/usr/bin/zapzap
/usr/share/%{name}

%changelog
* Thu Jul 25 2025 Rafael Tosta <rafael@example.com> - 1.0.0-1
- Primeira versão
