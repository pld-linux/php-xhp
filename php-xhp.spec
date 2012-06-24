#
# Conditional build:
%bcond_without	tests		# build without tests

%if "%{pld_release}" == "ac"
# add suffix, but allow ccache, etc in ~/.rpmmacros
%{expand:%%define	__cc	%(echo '%__cc' | sed -e 's,-gcc,-gcc4,')}
%{expand:%%define	__cxx	%(echo '%__cxx' | sed -e 's,-g++,-g++4,')}
%{expand:%%define	__cpp	%(echo '%__cpp' | sed -e 's,-gcc,-gcc4,')}
%endif

%define		modname	xhp
Summary:	Inline XML For PHP
Name:		php-%{modname}
Version:	1.3.9
Release:	4
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	http://github.com/facebook/xhp/tarball/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	38cab2551dc3a4e1bc5a68d2be39e64a
URL:		http://github.com/facebook/xhp/wiki
Patch0:		optflags.patch
%{?with_tests:BuildRequires:	/usr/bin/php}
# if you use git checkout:
#BuildRequires:	bison >= 2.3
#BuildRequires:	flex >= 2.5.35
BuildRequires:	libstdc++-devel >= 5:4.0
BuildRequires:	php-devel >= 3:5.2.0
%{?with_tests:BuildRequires:	php-pcre}
BuildRequires:	re2c >= 0.13.5
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpmbuild(macros) >= 1.519
%{?requires_php_extension}
# gcc4 might be installed, but not current __cc
%if "%(echo %{cc_version} | cut -d. -f1,2)" < "4.0"
BuildRequires:	__cc >= 4.0
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
XHP is a PHP extension which augments the syntax of the language such
that XML document fragments become valid PHP expressions. This allows
you to use PHP as a stricter templating engine and offers much more
straightforward implementation of reusable components.

%package devel
Summary:	Header files for xhp
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki xhp
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	php-devel >= 4:5.2.0

%description devel
Header files for xhp.

%prep
%setup -qc
mv facebook-%{modname}-*/* .
%patch0 -p1

%ifarch alpha sparc ppc
%{__sed} -i -e 's/-minline-all-stringops//' xhp/Makefile
%endif

%build
%{__make} -C xhp \
	libdir=%{_libdir} \
	CXX="%{__cxx}" \
	OPTFLAGS="%{rpmcxxflags}"

phpize
%configure
%{__make} \
	CC="%{__cc}" \
	CXX="%{__cxx}" \
	CXXFLAGS="%{rpmcxxflags}"

%if %{with tests}
cat <<'EOF' > run-tests.sh
#!/bin/sh
export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
unset TZ LANG LC_ALL || :
%{__make} test \
	RUN_TESTS_SETTINGS="-q $*"
EOF
chmod +x run-tests.sh
./run-tests.sh -w failed.log -s test.log
! test -s failed.log
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	INSTALL_HEADERS=xhp/xhp_preprocess.hpp \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

install -d $RPM_BUILD_ROOT%{php_data_dir}/xhp
cp -a php-lib/* $RPM_BUILD_ROOT%{php_data_dir}/xhp

install -d $RPM_BUILD_ROOT%{_libdir}
ln -s %{php_extensiondir}/libxhp.so $RPM_BUILD_ROOT%{_libdir}/libxhp.so

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
%{php_data_dir}/xhp

%files devel
%defattr(644,root,root,755)
%dir %{_includedir}/php/xhp
%{_includedir}/php/xhp/xhp_preprocess.hpp
%{_libdir}/libxhp.so
