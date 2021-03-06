# TODO
# - missing %%post %%service restart
#
# Conditional build:
%bcond_with	tests	# do not perform "make test"

Summary:	Python daemon that collects system metrics and publishes them to Graphite (and others)
Summary(pl.UTF-8):	Demon napisany w Pythonie, zbierający statystyki i publikujący je do Graphite (i innych)
Name:		diamond
Version:	4.0.195
Release:	2
License:	MIT
Group:		Libraries/Python
Source0:	https://pypi.python.org/packages/source/d/diamond/%{name}-%{version}.tar.gz
# Source0-md5:	b49da676079eafab3e784cccedc6bfa1
Source1:	%{name}.conf
Source3:	%{name}.init
Source10:	PostgresqlCollector.conf
URL:		https://github.com/python-diamond/Diamond
BuildRequires:	python-modules
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.710
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	python-configobj >= 5.0.6
Requires:	python-modules
Suggests:	python-setproctitle
Provides:	group(diamond)
Provides:	user(diamond)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Diamond is a python daemon that collects system metrics and publishes
them to Graphite (and others). It is capable of collecting cpu,
memory, network, i/o, load and disk metrics. Additionally, it features
an API for implementing custom collectors for gathering metrics from
almost any source.

%package -n %{name}-collector-postgresql
Summary:	Data collector for PostgreSQL database
Summary(pl.UTF-8):	Zbieracz statystyk dla bazdy danych Postgresql
Group:		Libraries/Python
Requires:	%{name} = %{version}-%{release}
Requires:	python-psycopg2

%description -n %{name}-collector-postgresql
Data collector for PostgreSQL database

%description -n %{name}-collector-postgresql -l pl.UTF-8
Zbieracz statystyk dla bazdy danych Postgresql

%prep
%setup -q

%build
%py_build %{?with_tests:test}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/{collectors,handlers} \
	$RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_localstatedir}/log/%{name}}

%py_install
%py_postclean

cp -p %{SOURCE1} $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}/diamond.conf
install -p %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/diamond
cp -p %{SOURCE10} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/collectors

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 327 diamond
%useradd -u 327 -d /var/log/diamond -g diamond -c "Diamond daemon user" diamond

%post
/sbin/chkconfig --add diamond

%preun
if [ "$1" = "0" ]; then
	%service diamond stop
	/sbin/chkconfig --del diamond
fi

%postun
if [ "$1" = "0" ]; then
	%userremove diamond
	%groupremove diamond
fi

%files
%defattr(644,root,root,755)
%doc README.md LICENSE
%dir %attr(750,root,diamond) %{_sysconfdir}/%{name}
%dir %attr(750,root,diamond) %{_sysconfdir}/%{name}/collectors
%dir %attr(750,root,diamond) %{_sysconfdir}/%{name}/handlers
%attr(640,root,diamond) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/diamond.conf
%attr(755,root,root) %{_bindir}/diamond
%attr(755,root,root) %{_bindir}/diamond-setup
%{py_sitescriptdir}/%{name}
%{_datadir}/diamond
%attr(750,diamond,diamond) /var/log/diamond
%attr(754,root,root) /etc/rc.d/init.d/diamond
%{py_sitescriptdir}/%{name}-%{version}-py*.egg-info

%files -n %{name}-collector-postgresql
%defattr(644,root,root,755)
%{_sysconfdir}/%{name}/collectors/PostgresqlCollector.conf
