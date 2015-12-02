# Conditional build:
# %bcond_with	doc	# don't build doc
# %bcond_with	tests	# do not perform "make test"
%bcond_without	python2 # CPython 2.x module
# %bcond_with	python3 # CPython 3.x module

%define 	module	diamond
Summary:	Python daemon that collects system metrics and publishes them to Graphite (and others).
Summary(pl.UTF-8):	Demon napisany w Pythonie, zbierający statystyki i publikujący je do Graphite (i innych)
# Name must match the python module/package name (as in 'import' statement)
Name:		diamond
Version:	4.0.195
Release:	0.5
License:	MIT
Group:		Libraries/Python
# https://github.com/python-diamond/Diamond/archive/v4.0.tar.gz
# https://pypi.python.org/packages/source/d/diamond/diamond-4.0.195.tar.gz#md5=b49da676079eafab3e784cccedc6bfa1
Source0:	https://pypi.python.org/packages/source/d/diamond/%{name}-%{version}.tar.gz
# Source0-md5:	b49da676079eafab3e784cccedc6bfa1
#URL:		https://pypi.python.org/pypi/MODULE
Source1:	%{name}.conf
Source3:	%{name}.init
Source10:	PostgresqlCollector.conf

URL:		https://github.com/python-diamond/Diamond
BuildRequires:	rpm-pythonprov
# for the py_build, py_install macros
BuildRequires:	rpmbuild(macros) >= 1.710
%if %{with python2}
BuildRequires:	python-modules
#BuildRequires:	python-setuptools
%endif
# %if %{with python3}
# #BuildRequires:	python3-setuptools
# BuildRequires:	python3-modules
# %endif
# when using /usr/bin/env or other in-place substitutions
#BuildRequires:	sed >= 4.0
# replace with other requires if defined in setup.py
Requires:	python-configobj >= 5.0.6
Requires:	python-modules
Suggests:	python-setproctitle
Provides:	group(diamond)
Provides:	user(diamond)

BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description

%description -l pl.UTF-8


%package -n %{module}-collector-postgresql
Summary:	Data collector for PostgreSQL database
Summary(pl.UTF-8):	Zbieracz statystyk dla bazdy danych Postgresql
Group:		Libraries/Python
Requires:	%{name}
Requires:	python-psycopg2

%description -n %{module}-collector-postgresql
Data collector for PostgreSQL database

%description -n %{module}-collector-postgresql -l pl.UTF-8
Zbieracz statystyk dla bazdy danych Postgresql

%prep
%setup -q -n %{module}-%{version}

# fix #!%{_bindir}/env python -> #!%{_bindir}/python:
#%{__sed} -i -e '1s,^#!.*python,#!%{__python},' %{name}.py

%build
%if %{with python2}
%py_build %{?with_tests:test}
%endif

# %if %{with python3}
# %%py3_build %{?with_tests:test}
# %endif

# %if %{with doc}
# cd docs
# %{__make} -j1 html
# rm -rf _build/html/_sources
# %endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with python2}
%py_install
%py_postclean
%endif
# %if %{with python3}
# %%py3_install
# %endif
install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{module}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{module}/collectors
install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{module}/handlers
## install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{module}/configs
install -p %{SOURCE1} $RPM_BUILD_ROOT/%{_sysconfdir}/%{module}/diamond.conf

install -d $RPM_BUILD_ROOT%{_localstatedir}/log/%{module}
# install -d $RPM_BUILD_ROOT%{_localstatedir}/run/carbon
# install -d $RPM_BUILD_ROOT%{_sharedstatedir}/carbon

install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install -p %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/diamond

install -p %{SOURCE10} $RPM_BUILD_ROOT%{_sysconfdir}/%{module}/collectors


%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 327 diamond
%useradd -u 327 -d /var/log/diamond -g diamond -c "Diamond daemon user" diamond

%postun
if [ "$1" = "0" ]; then
	%userremove diamond
	%groupremove diamond
fi

%if %{with python2}
%files
%defattr(644,root,root,755)
%doc README.md LICENSE
%dir %attr(750,root,diamond) %{_sysconfdir}/%{module}
%dir %attr(640,root,diamond) %{_sysconfdir}/%{module}/diamond.conf
%dir %attr(750,root,diamond) %{_sysconfdir}/%{module}/collectors
%dir %attr(750,root,diamond) %{_sysconfdir}/%{module}/handlers
%attr(755,root,root) %{_bindir}/diamond
%attr(755,root,root) %{_bindir}/diamond-setup
%{py_sitescriptdir}/%{module}
# %{py_sitescriptdir}/%{module}/collectors
%{_datadir}/diamond/
%attr(750,diamond,diamond) /var/log/diamond
%attr(754,root,root) /etc/rc.d/init.d/diamond


%if "%{py_ver}" > "2.4"
%{py_sitescriptdir}/%{module}-%{version}-py*.egg-info
%endif
%endif

# %if %{with python3}
# %files -n python3-%{module}
# %defattr(644,root,root,755)
# %doc AUTHORS CHANGES LICENSE
# %{py3_sitescriptdir}/%{module}
# %{py3_sitescriptdir}/%{module}-%{version}-py*.egg-info
# %{_examplesdir}/python3-%{module}-%{version}
# %endif
#
# %if %{with doc}
# %files apidocs
# %defattr(644,root,root,755)
# %doc docs/_build/html/*
# %endif

%files -n %{module}-collector-postgresql
%defattr(644,root,root,755)
%{_sysconfdir}/%{module}/collectors/PostgresqlCollector.conf
