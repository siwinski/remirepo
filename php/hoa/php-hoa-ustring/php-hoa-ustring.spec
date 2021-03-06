# remirepo/fedora spec file for php-hoa-ustring
#
# Copyright (c) 2016 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%global bootstrap    1
%global gh_commit    9f76b9aae5901b4f476ef854e29ccd746d6899d2
#global gh_date      20150728
%global gh_short     %(c=%{gh_commit}; echo ${c:0:7})
%global gh_owner     hoaproject
%global gh_project   Ustring
%global php_home     %{_datadir}/php
%global ns_vendor    Hoa
%global ns_project   Ustring
%global pk_vendor    hoa
%global pk_project   ustring
%if %{bootstrap}
%global with_tests   0%{?_with_tests:1}
%else
%global with_tests   0%{!?_without_tests:1}
%endif

Name:           php-%{pk_vendor}-%{pk_project}
Version:        4.16.01.11
%global specrel 0
Release:        %{?gh_date:0.%{specrel}.%{?prever}%{!?prever:%{gh_date}git%{gh_short}}}%{!?gh_date:%{specrel}}%{?dist}
Summary:        The %{ns_vendor}\%{ns_project} library.

Group:          Development/Libraries
License:        BSD
URL:            https://github.com/%{gh_owner}/%{gh_project}
Source0:        https://github.com/%{gh_owner}/%{gh_project}/archive/%{gh_commit}/%{name}-%{version}-%{gh_short}.tar.gz
Source1:        %{name}-autoload.php
Source2:        http://hoa-project.net/LICENSE

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
%if %{with_tests}
BuildRequires:  php-composer(%{pk_vendor}/consistency)     >= 1.0
BuildRequires:  php-composer(%{pk_vendor}/exception)       >= 1.0
# From composer.json, "require-dev": {
#        "hoa/test": "~2.0"
BuildRequires:  php-composer(%{pk_vendor}/test)            >= 2.0
%endif

# from composer.json, "require": {
#        "hoa/consistency": "~1.0",
#        "hoa/exception"  : "~1.0"
Requires:       php-composer(%{pk_vendor}/consistency)     >= 1.0
Requires:       php-composer(%{pk_vendor}/consistency)     <  2
Requires:       php-composer(%{pk_vendor}/exception)       >= 1.0
Requires:       php-composer(%{pk_vendor}/exception)       <  2
# from composer.json, "suggest": {
#        "ext-iconv": "ext/iconv must be present (or a third implementation) to use Hoa\\Ustring::transcode().",
#        "ext-intl" : "To get a better Hoa\\Ustring::toAscii() and Hoa\\Ustring::compareTo()."
Requires:       php-iconv
Requires:       php-intl
# from phpcompatinfo report for version 4.16.01.11
Requires:       php-mbstring
Requires:       php-pcre
Requires:       php-spl

Provides:       php-composer(%{pk_vendor}/%{pk_project}) = %{version}


%description
The %{ns_vendor}\%{ns_project} library allows to manipulate
UTF-8 strings easily with some search algorithms.

Autoloader: %{php_home}/%{ns_vendor}/%{ns_project}/autoload.php


%prep
%setup -q -n %{gh_project}-%{gh_commit}
cp %{SOURCE1} autoload.php
cp %{SOURCE2} LICENSE

%build
: Nothing

%install
rm -rf      %{buildroot}
mkdir -p    %{buildroot}%{php_home}/%{ns_vendor}/%{ns_project}
cp -pr *php %{buildroot}%{php_home}/%{ns_vendor}/%{ns_project}/
find . -mindepth 1 -maxdepth 1 -type d \! \( -name Test -o -name Documentation \) -print -exec \
  cp -pr {}  %{buildroot}%{php_home}/%{ns_vendor}/%{ns_project} \; \


%check
%if %{with_tests}
%else
: bootstrap build with test suite disabled
%endif


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc composer.json
%doc *md
%{php_home}/%{ns_vendor}/%{ns_project}


%changelog
* Wed Apr  6 2016 Remi Collet <remi@fedoraproject.org> - 4.16.01.11-0
- initial package
- bootstrap build

