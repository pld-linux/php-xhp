#
# Conditional build:
%bcond_without	tests		# build without tests

%define		modname	xhp
Summary:	Inline XML For PHP
Name:		php-%{modname}
Version:	1.3.8
Release:	1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	http://github.com/facebook/xhp/tarball/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	3abc2cdb5ba57594db7c4d7445c6000d
URL:		http://wiki.github.com/facebook/xhp/
BuildRequires:	bison >= 2.3
BuildRequires:	flex >= 2.5.35
BuildRequires:	gcc >= 6:4.0
BuildRequires:	php-devel >= 3:5.2.0
BuildRequires:	re2c >= 0.13.5
BuildRequires:	rpmbuild(macros) >= 1.519
%{?requires_php_extension}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
XHP is a PHP extension which augments the syntax of the language such
that XML document fragments become valid PHP expressions. This allows
you to use PHP as a stricter templating engine and offers much more
straightforward implementation of reusable components.

%prep
%setup -qc
mv facebook-%{modname}-*/* .

%build
phpize
%configure
%{__make} \
	CXX="%{__cxx}" \
	CPPFLAGS="-fPIC %{rpmcxxflags} -minline-all-stringops"

%{?with_tests:%{__make} test}}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d

%{__make} install \
	INSTALL_ROOT=$RPM_BUILD_ROOT \
	EXTENSION_DIR=%{php_extensiondir}
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc INSTALL
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
