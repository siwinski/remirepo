# remimrepo/fedora spec file for php-pecl-stomp
#
# Copyright (c) 2014-2016 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%{?scl:          %scl_package         php-pecl-stomp}
%{!?scl:         %global _root_prefix %{_prefix}}

%global with_zts    0%{!?_without_zts:%{?__ztsphp:1}}
%global pecl_name   stomp
%global ini_name    40-%{pecl_name}.ini

Summary:        Stomp client extension
Name:           %{?scl_prefix}php-pecl-%{pecl_name}
Version:        2.0.0
Release:        2%{?dist}%{!?nophptag:%(%{__php} -r 'echo ".".PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')}
License:        PHP
Group:          Development/Languages
URL:            http://pecl.php.net/package/%{pecl_name}
Source0:        http://pecl.php.net/get/%{pecl_name}-%{version}.tgz

Patch0:         %{pecl_name}-upstream.patch

BuildRequires:  %{?scl_prefix}php-devel > 7
BuildRequires:  %{?scl_prefix}php-pear
BuildRequires:  openssl-devel

Requires:       %{?scl_prefix}php(zend-abi) = %{php_zend_api}
Requires:       %{?scl_prefix}php(api) = %{php_core_api}
%{?_sclreq:Requires: %{?scl_prefix}runtime%{?_sclreq}%{?_isa}}

Provides:       %{?scl_prefix}php-%{pecl_name}               = %{version}
Provides:       %{?scl_prefix}php-%{pecl_name}%{?_isa}       = %{version}
Provides:       %{?scl_prefix}php-pecl(%{pecl_name})         = %{version}
Provides:       %{?scl_prefix}php-pecl(%{pecl_name})%{?_isa} = %{version}
%if "%{?scl_prefix}" != "%{?sub_prefix}"
Provides:       %{?scl_prefix}php-pecl-%{pecl_name}          = %{version}-%{release}
Provides:       %{?scl_prefix}php-pecl-%{pecl_name}%{?_isa}  = %{version}-%{release}
%endif

%if "%{?vendor}" == "Remi Collet" && 0%{!?scl:1}
# Other third party repo stuff
Obsoletes:     php53-pecl-%{pecl_name}  <= %{version}
Obsoletes:     php53u-pecl-%{pecl_name} <= %{version}
Obsoletes:     php54-pecl-%{pecl_name}  <= %{version}
Obsoletes:     php54w-pecl-%{pecl_name} <= %{version}
Obsoletes:     php55u-pecl-%{pecl_name} <= %{version}
Obsoletes:     php55w-pecl-%{pecl_name} <= %{version}
Obsoletes:     php56u-pecl-%{pecl_name} <= %{version}
Obsoletes:     php56w-pecl-%{pecl_name} <= %{version}
Obsoletes:     php70u-pecl-%{pecl_name} <= %{version}
Obsoletes:     php70w-pecl-%{pecl_name} <= %{version}
%if "%{php_version}" > "7.1"
Obsoletes:     php71u-pecl-%{pecl_name} <= %{version}
Obsoletes:     php71w-pecl-%{pecl_name} <= %{version}
%endif
%endif

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter shared private
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
This extension allows php applications to communicate with any
Stomp compliant Message Brokers through easy object oriented
and procedural interfaces.

Documentation: http://php.net/stomp

Package built for PHP %(%{__php} -r 'echo PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')%{?scl: as Software Collection (%{scl} by %{?scl_vendor}%{!?scl_vendor:rh})}.


%prep
%setup -q -c
mv %{pecl_name}-%{version} NTS

# Don't install/register tests
sed -e 's/role="test"/role="src"/' \
    %{?_licensedir:-e '/LICENSE/s/role="doc"/role="src"/' } \
    -i package.xml

cd NTS
%patch0 -p1 -b .upstream

# Sanity check, really often broken
extver=$(sed -n '/#define PHP_STOMP_VERSION/{s/.* "//;s/".*$//;p}' php_stomp.h)
if test "x${extver}" != "x%{version}%{?versuf}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}%{?versuf}.
   exit 1
fi
cd ..


%if %{with_zts}
# Duplicate source tree for NTS / ZTS build
cp -pr NTS ZTS
%endif

# Create configuration file
cat << 'EOF' | tee %{ini_name}
; Enable %{summary} module
extension=%{pecl_name}.so

; See http://php.net/manual/en/stomp.configuration.php
;stomp.default_broker = "tcp://localhost:61613"
;stomp.default_username = ''
;stomp.default_password = ''
;stomp.default_read_timeout_sec = 2
;stomp.default_read_timeout_usec = 0
;stomp.default_connection_timeout_sec = 2
;stomp.default_connection_timeout_usec = 0
EOF


%build
peclbuild() {
%configure \
    --enable-stomp \
    --with-openssl-dir=%{_root_prefix} \
    --with-libdir=%{_lib} \
    --with-php-config=$1

make %{?_smp_mflags}
}

cd NTS
%{_bindir}/phpize
peclbuild %{_bindir}/php-config

%if %{with_zts}
cd ../ZTS
%{_bindir}/zts-phpize
peclbuild %{_bindir}/zts-php-config
%endif


%install
make -C NTS install INSTALL_ROOT=%{buildroot}

# install config file
install -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

%if %{with_zts}
make -C ZTS install INSTALL_ROOT=%{buildroot}

install -D -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

# Documentation
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%if 0%{?fedora} < 24
# when pear installed alone, after us
%triggerin -- %{?scl_prefix}php-pear
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

# posttrans as pear can be installed after us
%posttrans
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

%postun
if [ $1 -eq 0 -a -x %{__pecl} ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi
%endif


%check
# Upstream test suite requires a Stomp server

: Minimal load test for NTS extension
%{__php} --no-php-ini \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep -i %{pecl_name}

%if %{with_zts}
: Minimal load test for ZTS extension
%{__ztsphp} --no-php-ini \
    --define extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
    --modules | grep -i %{pecl_name}
%endif


%files
%{?_licensedir:%license NTS/LICENSE}
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so

%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
* Fri Jun 10 2016 Remi Collet <remi@fedoraproject.org> - 2.0.0-2
- add upstream patch for PHP 7.1

* Thu May 26 2016 Remi Collet <remi@fedoraproject.org> - 2.0.0-1
- update to 2.0.0 (php 7, beta)

* Tue Mar  8 2016 Remi Collet <remi@fedoraproject.org> - 1.0.9-2
- adapt for F24

* Tue Jan 05 2016 Remi Collet <remi@fedoraproject.org> - 1.0.9-1
- Update to 1.0.9 (stable)

* Tue May 19 2015 Remi Collet <remi@fedoraproject.org> - 1.0.8-1
- Update to 1.0.8 (stable, no change)

* Sat May 16 2015 Remi Collet <remi@fedoraproject.org> - 1.0.7-1
- Update to 1.0.7 (stable)
- drop runtime dependency on pear, new scriptlets

* Wed Dec 24 2014 Remi Collet <remi@fedoraproject.org> - 1.0.6-2.1
- Fedora 21 SCL mass rebuild

* Mon Dec 08 2014 Remi Collet <remi@fedoraproject.org> - 1.0.6-2
- Update to 1.0.6 (stable)
- enable openssl support

* Fri Oct 10 2014 Remi Collet <remi@fedoraproject.org> - 1.0.5-1
- initial package, version 1.0.5 (stable)
