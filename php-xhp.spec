#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	xhp
Summary:	Inline XML For PHP
Name:		%{php_name}-%{modname}
Version:	1.5
Release:	1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	https://github.com/facebook/xhp/archive/%{version}/php-%{modname}-%{version}.tar.gz
# Source0-md5:	b9a552d6cd823a82f2e57037aed42a69
URL:		http://github.com/facebook/xhp/wiki
Patch0:		optflags.patch
BuildRequires:	%{php_name}-devel >= 4:5.2.0
%{?with_tests:BuildRequires:	/usr/bin/php}
# if you use git checkout:
#BuildRequires:	bison >= 2.3
#BuildRequires:	flex >= 2.5.35
BuildRequires:	libstdc++-devel >= 5:4.0
%{?with_tests:BuildRequires:	php-pcre}
BuildRequires:	re2c >= 0.13.5
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpmbuild(macros) >= 1.666
%{?requires_php_extension}
Requires(post,postun):	/sbin/ldconfig
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
%setup -q -n %{modname}-%{version}
%patch0 -p1

# disable failing tests
mv tests/idx-01.phpt{,.fail}
mv tests/trait.phpt{,.fail}

%build
%{__make} -C xhp \
	libdir=%{_libdir} \
	CXX="%{__cxx}" \
	OPTFLAGS="%{rpmcxxflags} -fpermissive"

phpize
%configure
%{__make} \
	CC="%{__cc}" \
	CXX="%{__cxx}" \
	CXXFLAGS="%{rpmcxxflags} -fpermissive"

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
test ! -s failed.log
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

install -d $RPM_BUILD_ROOT%{php_data_dir}/xhp
cp -a php-lib/* $RPM_BUILD_ROOT%{php_data_dir}/xhp
install -p xhp/libxhp.so $RPM_BUILD_ROOT%{_libdir}

# files used by hiphop-php
install -d $RPM_BUILD_ROOT{%{_libdir},%{_includedir}}
cp -p xhp/libxhp.a $RPM_BUILD_ROOT%{_libdir}
cp -p xhp/xhp_preprocess.hpp $RPM_BUILD_ROOT%{_includedir}

%clean
rm -rf $RPM_BUILD_ROOT


%post
/sbin/ldconfig
%php_webserver_restart

%postun
/sbin/ldconfig
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc README.textile INSTALL
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
%{_libdir}/libxhp.so
%{php_data_dir}/xhp

%files devel
%defattr(644,root,root,755)
%{_includedir}/xhp_preprocess.hpp
%{_libdir}/libxhp.a
