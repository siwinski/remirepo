# remirepo spec file for php-doctrine-dbal, from Fedora:
#
# Fedora spec file for php-doctrine-dbal
#
# Copyright (c) 2013-2016 Shawn Iwinski <shawn.iwinski@gmail.com>
#                         Adam Williamson <awilliam@redhat.com>
#
# License: MIT
# http://opensource.org/licenses/MIT
#
# Please preserve changelog entries
#

%global github_owner     doctrine
%global github_name      dbal
%global github_version   2.5.4
%global github_commit    abbdfd1cff43a7b99d027af3be709bc8fc7d4769

%global composer_vendor  doctrine
%global composer_project dbal

# "php": ">=5.3.2"
%global php_min_ver 5.3.2
# "doctrine/common": ">=2.4,<2.7-dev"
#     NOTE: Min version not 2.4 because autoloader required
%global doctrine_common_min_ver 2.5.0
%global doctrine_common_max_ver 2.7
# "symfony/console": "2.*"
%global symfony_console_min_ver 2.0
%global symfony_console_max_ver 3.0

%{!?phpdir:  %global phpdir  %{_datadir}/php}

%if 0%{?rhel} == 5
# No test as no SQlite3 ext
%global with_tests 0
%else
# Build using "--without tests" to disable tests
%global with_tests 0%{!?_without_tests:1}
%endif

Name:          php-%{composer_vendor}-%{composer_project}
Version:       %{github_version}
Release:       1%{?github_release}%{?dist}
Summary:       Doctrine Database Abstraction Layer (DBAL)

Group:         Development/Libraries
License:       MIT
URL:           http://www.doctrine-project.org/projects/dbal.html

# Run "php-doctrine-dbal-get-source.sh" to create source
Source0:       %{name}-%{version}-%{github_commit}.tar.gz
Source1:       %{name}-get-source.sh

# Update bin script:
# 1) Add she-bang
# 2) Auto-load using Doctrine\Common\ClassLoader
Patch0:        %{name}-bin.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch
# Tests
%if %{with_tests}
BuildRequires: php-composer(phpunit/phpunit)
## composer.json
BuildRequires: php(language)                 >= %{php_min_ver}
BuildRequires: php-composer(doctrine/common) >= %{doctrine_common_min_ver}
BuildRequires: php-composer(doctrine/common) <  %{doctrine_common_max_ver}
## composer.json (optional)
BuildRequires: php-composer(symfony/console) >= %{symfony_console_min_ver}
BuildRequires: php-composer(symfony/console) <  %{symfony_console_max_ver}
## phpcompatinfo (computed from version 2.5.4)
BuildRequires: php-date
BuildRequires: php-json
BuildRequires: php-pcre
BuildRequires: php-pdo
BuildRequires: php-reflection
BuildRequires: php-spl
%endif

# composer.json
Requires:      php(language)                 >= %{php_min_ver}
Requires:      php-composer(doctrine/common) >= %{doctrine_common_min_ver}
Requires:      php-composer(doctrine/common) <  %{doctrine_common_max_ver}
# composer.json (optional)
Requires:      php-composer(symfony/console) >= %{symfony_console_min_ver}
Requires:      php-composer(symfony/console) <  %{symfony_console_max_ver}
# phpcompatinfo (computed from version 2.5.4)
Requires:      php-date
Requires:      php-json
Requires:      php-pcre
Requires:      php-pdo
Requires:      php-reflection
Requires:      php-spl

# Composer
Provides:      php-composer(%{composer_vendor}/%{composer_project}) = %{version}
# PEAR
Provides:      php-pear(pear.doctrine-project.org/DoctrineDBAL) = %{version}
# Rename
Obsoletes:     php-doctrine-DoctrineDBAL < %{version}
Provides:      php-doctrine-DoctrineDBAL = %{version}

%description
The Doctrine database abstraction & access layer (DBAL) offers a lightweight
and thin runtime layer around a PDO-like API and a lot of additional, horizontal
features like database schema introspection and manipulation through an OO API.

The fact that the Doctrine DBAL abstracts the concrete PDO API away through the
use of interfaces that closely resemble the existing PDO API makes it possible
to implement custom drivers that may use existing native or self-made APIs. For
example, the DBAL ships with a driver for Oracle databases that uses the oci8
extension under the hood.

Autoloader: %{phpdir}/Doctrine/DBAL/autoload.php


%prep
%setup -qn %{github_name}-%{github_commit}

: Patch bin script
%patch0 -p1

: Remove empty file
rm -f lib/Doctrine/DBAL/README.markdown

: Create autoloader
cat <<'AUTOLOAD' | tee lib/Doctrine/DBAL/autoload.php
<?php
/**
 * Autoloader for %{name} and its' dependencies
 * (created by %{name}-%{version}-%{release}).
 *
 * @return \Symfony\Component\ClassLoader\ClassLoader
 */

if (!isset($fedoraClassLoader) || !($fedoraClassLoader instanceof \Symfony\Component\ClassLoader\ClassLoader)) {
    if (!class_exists('Symfony\\Component\\ClassLoader\\ClassLoader', false)) {
        require_once '%{phpdir}/Symfony/Component/ClassLoader/ClassLoader.php';
    }

    $fedoraClassLoader = new \Symfony\Component\ClassLoader\ClassLoader();
    $fedoraClassLoader->register();
}

$fedoraClassLoader->addPrefix('Doctrine\\DBAL\\', dirname(dirname(__DIR__)));

// Required dependencies
require_once '%{phpdir}/Doctrine/Common/autoload.php';
require_once '%{phpdir}/Symfony/Component/Console/autoload.php';

return $fedoraClassLoader;
AUTOLOAD


%build
# Empty build section, nothing required


%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/%{phpdir}
cp -rp lib/Doctrine %{buildroot}/%{phpdir}/

mkdir -p %{buildroot}/%{_bindir}
install -pm 0755 bin/doctrine-dbal.php %{buildroot}/%{_bindir}/doctrine-dbal


%check
%if %{with_tests}
# Rewrite "tests/Doctrine/Tests/TestInit.php" (aka PHPUnit bootstrap)
mv tests/Doctrine/Tests/TestInit.php tests/Doctrine/Tests/TestInit.php.dist
cat > tests/Doctrine/Tests/TestInit.php <<'BOOTSTRAP'
<?php
$fedoraClassLoader =
    require_once '%{buildroot}/%{phpdir}/Doctrine/DBAL/autoload.php';

$fedoraClassLoader->addPrefix(
    'Doctrine\\Tests\\',
    dirname(dirname(dirname(__DIR__))).'/tests'
);
BOOTSTRAP

%{_bindir}/phpunit

if which php70; then
   php70 %{_bindir}/phpunit
fi
%else
: Tests skipped
%endif


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc *.md
%doc composer.json
%{phpdir}/Doctrine/DBAL
%{_bindir}/doctrine-dbal


%changelog
* Mon Mar 14 2016 Shawn Iwinski <shawn.iwinski@gmail.com> - 2.5.4-1
- Updated to 2.5.4 (RHBZ #1153987)
- Added autoloader

* Wed Jan 14 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 2.5.1-1
- Updated to 2.5.1 (BZ #1153987)

* Fri Jan 02 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 2.5.1-0.2.20150101git185b886
- Updated to latest snapshot
- Fixed bin script
- Added tests

* Thu Jul 31 2014 Remi Collet <rpms@famillecollet.com> 2.4.2-6
- backport for remi repo
- fix license handling

* Tue Jul 29 2014 Adam Williamson <awilliam@redhat.com> - 2.4.2-6
- really apply the patch

* Tue Jul 29 2014 Adam Williamson <awilliam@redhat.com> - 2.4.2-5
- backport another OwnCloud-related pgsql fix from upstream master

* Fri Jun 20 2014 Shawn Iwinski <shawn.iwinski@gmail.com> - 2.4.2-4
- Added php-composer(%%{composer_vendor}/%%{composer_project}) virtual provide
- Updated Doctrine dependencies to use php-composer virtual provides

* Sat Jan 11 2014 Remi Collet <rpms@famillecollet.com> 2.4.2-2
- backport for remi repo

* Tue Jan 07 2014 Adam Williamson <awilliam@redhat.com> - 2.4.2-2
- primary_index: one OwnCloud patch still isn't in upstream

* Sat Jan 04 2014 Shawn Iwinski <shawn.iwinski@gmail.com> 2.4.2-1
- Updated to 2.4.2
- Conditional %%{?dist}

* Tue Dec 31 2013 Shawn Iwinski <shawn.iwinski@gmail.com> 2.4.1-2.20131231gitd08b11c
- Updated to latest snapshot
- Removed patches (pulled into latest snapshot)

* Sun Dec 29 2013 Shawn Iwinski <shawn.iwinski@gmail.com> 2.4.1-1
- Initial package
