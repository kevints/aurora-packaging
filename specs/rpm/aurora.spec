#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Overridable variables;
%if %{?!AURORA_VERSION:1}0
%global AURORA_VERSION 0.9.0
%endif

%if %{?!AURORA_USER:1}0
%global AURORA_USER aurora
%endif

%if %{?!AURORA_GROUP:1}0
%global AURORA_GROUP aurora
%endif

%if %{?!GRADLE_BASEURL:1}0
%global GRADLE_BASEURL https://services.gradle.org/distributions
%endif

%if %{?!GRADLE_VERSION:1}0
%global GRADLE_VERSION 2.6
%endif

%if %{?!JAVA_VERSION:!}0
%global JAVA_VERSION 1.8.0
%endif

%if %{?!MESOS_VERSION:1}0
%global MESOS_VERSION 0.23.0
%endif

%if %{?!PEX_BINARIES:1}0
%global PEX_BINARIES aurora aurora_admin thermos thermos_executor thermos_runner thermos_observer
%endif

%if %{?!PYTHON_VERSION:1}0
%global PYTHON_VERSION 2.7
%endif

Name:          aurora-scheduler
Version:       %{AURORA_VERSION}
Release:       1%{?dist}.aurora
Summary:       The Apache Aurora Scheduler
Group:         Applications/System
License:       ASL 2.0
URL:           https://%{name}.apache.org/

#Source0:       https://github.com/apache/%{name}/archive/%{version}/aurora.tar.gz
Source0:       aurora.tar.gz
Source1:       aurora.service
Source2:       thermos-observer.service
Source3:       aurora.init.sh
Source4:       thermos-observer.init.sh
Source5:       aurora.startup.sh
Source6:       thermos-observer.startup.sh
Source7:       aurora.sysconfig
Source8:       thermos-observer.sysconfig
Source9:       aurora.logrotate
Source10:      thermos-observer.logrotate
Source11:      clusters.json

BuildRequires: apr-devel
BuildRequires: cyrus-sasl-devel
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: git
BuildRequires: java-%{JAVA_VERSION}-openjdk-devel
BuildRequires: krb5-devel
BuildRequires: libcurl-devel
BuildRequires: patch
%if 0%{?rhel} && 0%{?rhel} < 7
BuildRequires: python27
BuildRequires: python27-scldevel
%else
BuildRequires: python
BuildRequires: python-devel
%endif
BuildRequires: subversion-devel
BuildRequires: tar
BuildRequires: unzip
BuildRequires: wget
BuildRequires: zlib-devel

%if 0%{?rhel} && 0%{?rhel} < 7
Requires:      daemonize
%endif
Requires:      java-%{JAVA_VERSION}
Requires:      mesos = %{MESOS_VERSION}


%description -n aurora-scheduler
Apache Aurora lets you use an Apache Mesos cluster as a private cloud. It supports running
long-running services, cron jobs, and ad-hoc jobs.

Aurora aims to make it extremely quick and easy to take a built application and run it on
machines in a cluster, with an emphasis on reliability. It provides basic operations to manage
services running in a cluster, such as rolling upgrades.

To very concisely describe Aurora, it is a system that you can instruct to do things like run
100 of these, somewhere, forever.

This package contains the Aurora scheduler. This package is typically installed on 3 to 5 nodes
per Mesos cluster.


%package -n aurora-tools
Summary: The Apache Aurora client and admin client tools
Group: Development/Tools

Requires: krb5-libs
%if 0%{?rhel} && 0%{?rhel} < 7
Requires: python27
%else
Requires: python
%endif

%description -n aurora-tools
Apache Aurora lets you use an Apache Mesos cluster as a private cloud. It supports running
long-running services, cron jobs, and ad-hoc jobs.

Aurora aims to make it extremely quick and easy to take a built application and run it on
machines in a cluster, with an emphasis on reliability. It provides basic operations to manage
services running in a cluster, such as rolling upgrades.

To very concisely describe Aurora, it is a system that you can instruct to do things like run
100 of these, somewhere, forever.

This package includes the aurora and aurora-admin commandline tools for interacting with
the Aurora scheduler. This package is typically installed on cluster user and administrator
workstations.

%package -n aurora-executor
Summary: The Apache Aurora Executor and Observer components
Group: Applications/System

Requires: cyrus-sasl
%if 0%{?rhel} && 0%{?rhel} < 7
Requires: daemonize
Requires: docker-io
%else
Requires: docker
%endif
Requires: mesos = %{MESOS_VERSION}
%if 0%{?rhel} && 0%{?rhel} < 7
Requires: python27
%else
Requires: python
%endif

%description -n aurora-executor
Apache Aurora lets you use an Apache Mesos cluster as a private cloud. It supports running
long-running services, cron jobs, and ad-hoc jobs.

Aurora aims to make it extremely quick and easy to take a built application and run it on
machines in a cluster, with an emphasis on reliability. It provides basic operations to manage
services running in a cluster, such as rolling upgrades.

To very concisely describe Aurora, it is a system that you can instruct to do things like run
100 of these, somewhere, forever.

This package contains the components necessary to run Aurora jobs on a Mesos Agent node: the
Aurora Executor and Observer. This package is typically installed on every Mesos Agent node
in a cluster.

%prep
%setup -n apache-aurora-%{version}


%build
# Preferences SCL-installed Python 2.7 if we're building on EL6.
%if 0%{?rhel} && 0%{?rhel} < 7
export PATH=/opt/rh/python27/root/usr/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/opt/rh/python27/root/usr/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
export MANPATH=/opt/rh/python27/root/usr/share/man:${MANPATH}
# For systemtap
export XDG_DATA_DIRS=/opt/rh/python27/root/usr/share${XDG_DATA_DIRS:+:${XDG_DATA_DIRS}}
# For pkg-config
export PKG_CONFIG_PATH=/opt/rh/python27/root/usr/lib64/pkgconfig${PKG_CONFIG_PATH:+:${PKG_CONFIG_PATH}}
%endif

# Preferences Java 1.8 over any other Java version.
export PATH=/usr/lib/jvm/java-1.8.0/bin:${PATH}

# Downloads Gradle executable.
wget %{GRADLE_BASEURL}/gradle-%{GRADLE_VERSION}-bin.zip
unzip gradle-%{GRADLE_VERSION}-bin.zip

# Builds the Aurora scheduler.
./gradle-%{GRADLE_VERSION}/bin/gradle installDist

# Configures pants to use our distributed platform-specific eggs.
# This avoids building mesos to produce them.
export PANTS_CONFIG_OVERRIDE=/pants.ini

# Builds Aurora client PEX binaries.
./pants binary src/main/python/apache/aurora/kerberos:kaurora
mv dist/kaurora.pex dist/aurora.pex
./pants binary src/main/python/apache/aurora/kerberos:kaurora_admin
mv dist/kaurora_admin.pex dist/aurora_admin.pex

# Builds Aurora Thermos and GC executor PEX binaries.
./pants binary src/main/python/apache/aurora/executor:thermos_executor
./pants binary src/main/python/apache/aurora/tools:thermos
./pants binary src/main/python/apache/aurora/tools:thermos_observer
./pants binary src/main/python/apache/thermos/runner:thermos_runner

# Packages the Thermos runner within the Thermos Executor.
build-support/embed_runner_in_executor.py

%install -n aurora-scheduler
rm -rf $RPM_BUILD_ROOT

# Builds installation directory structure.
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_docdir}/%{name}-%{version}
mkdir -p %{buildroot}%{_prefix}/lib/%{name}
mkdir -p %{buildroot}%{_sharedstatedir}
mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}
mkdir -p %{buildroot}%{_localstatedir}/log/thermos
mkdir -p %{buildroot}%{_localstatedir}/run/thermos
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/init.d
mkdir -p %{buildroot}%{_sysconfdir}/systemd/system
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig

# Installs the Aurora scheduler that was just built into /usr/lib/aurora.
cp -r dist/install/aurora-scheduler/* %{buildroot}%{_prefix}/lib/%{name}

# Installs all PEX binaries.
for pex_binary in %{PEX_BINARIES}; do
  install -m 755 dist/${pex_binary}.pex %{buildroot}%{_bindir}/${pex_binary}
done

# Installs all support scripting.
%if 0%{?fedora} || 0%{?rhel} > 6
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/systemd/system
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/systemd/system/thermos-observer.service
%else
install -m 755 %{SOURCE3} %{buildroot}%{_sysconfdir}/init.d/aurora
install -m 755 %{SOURCE4} %{buildroot}%{_sysconfdir}/init.d/thermos-observer
%endif

install -m 755 %{SOURCE5} %{buildroot}%{_bindir}/%{name}-scheduler-startup
install -m 755 %{SOURCE6} %{buildroot}%{_bindir}/thermos-observer-startup

install -m 644 %{SOURCE7} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
install -m 644 %{SOURCE8} %{buildroot}%{_sysconfdir}/sysconfig/thermos-observer

install -m 644 %{SOURCE9} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -m 644 %{SOURCE10} %{buildroot}%{_sysconfdir}/logrotate.d/thermos-observer

install -m 644 %{SOURCE11} %{buildroot}%{_sysconfdir}/%{name}/clusters.json


%pre -n aurora-scheduler
getent group %{AURORA_GROUP} > /dev/null || groupadd -r %{AURORA_GROUP}
getent passwd %{AURORA_USER} > /dev/null || \
    useradd -r -d %{_localstatedir}/lib/%{name} -g %{AURORA_GROUP} \
    -s /bin/bash -c "Aurora Scheduler" %{AURORA_USER}
exit 0

# Pre/post installation scripts:
%post -n aurora-scheduler
%if 0%{?fedora} || 0%{?rhel} > 6
%systemd_post %{name}.service
%else
/sbin/chkconfig --add %{name}
%endif

%preun -n aurora-scheduler
%if 0%{?fedora} || 0%{?rhel} > 6
%systemd_preun %{name}.service
%else
/sbin/service %{name} stop >/dev/null 2>&1
/sbin/chkconfig --del %{name}
%endif

%postun -n aurora-scheduler
%if 0%{?fedora} || 0%{?rhel} > 6
%systemd_postun_with_restart %{name}.service
%else
/sbin/service %{name} start >/dev/null 2>&1
%endif


%post -n aurora-executor
%if 0%{?fedora} || 0%{?rhel} > 6
%systemd_post thermos-observer.service
%else
/sbin/chkconfig --add thermos-observer
%endif

%preun -n aurora-executor
%if 0%{?fedora} || 0%{?rhel} > 6
%systemd_preun thermos-observer.service
%else
/sbin/service thermos-observer stop >/dev/null 2>&1
/sbin/chkconfig --del thermos-observer
%endif

%postun -n aurora-executor
%if 0%{?fedora} || 0%{?rhel} > 6
%systemd_postun_with_restart thermos-observer.service
%else
/sbin/service thermos-observer start >/dev/null 2>&1
%endif


%files -n aurora-scheduler
%defattr(-,root,root,-)
%doc docs/*.md
%{_bindir}/aurora-scheduler-startup
%attr(-,%{AURORA_USER},%{AURORA_GROUP}) %{_localstatedir}/lib/%{name}
%attr(-,%{AURORA_USER},%{AURORA_GROUP}) %{_localstatedir}/log/%{name}
%{_prefix}/lib/%{name}/bin/*
%{_prefix}/lib/%{name}/etc/*
%{_prefix}/lib/%{name}/lib/*
%if 0%{?fedora} || 0%{?rhel} > 6
%{_sysconfdir}/systemd/system/%{name}.service
%else
%{_sysconfdir}/init.d/%{name}
%endif
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}


%files -n aurora-tools
%defattr(-,root,root,-)
%{_bindir}/%{name}
%{_bindir}/%{name}_admin
%config(noreplace) %{_sysconfdir}/%{name}/clusters.json


%files -n aurora-executor
%defattr(-,root,root,-)
%{_bindir}/thermos
%{_bindir}/thermos_executor
%{_bindir}/thermos_observer
%{_bindir}/thermos_runner
%{_bindir}/thermos-observer-startup
%{_localstatedir}/log/thermos
%{_localstatedir}/run/thermos
%if 0%{?fedora} || 0%{?rhel} > 6
%{_sysconfdir}/systemd/system/thermos-observer.service
%else
%{_sysconfdir}/init.d/thermos-observer
%endif
%config(noreplace) %{_sysconfdir}/logrotate.d/thermos-observer
%config(noreplace) %{_sysconfdir}/sysconfig/thermos-observer


%changelog
* Mon Aug 31 2015 Bill Farner <wfarner@apache.org> 0.9.0-1.el7
- Apache Aurora 0.9.0
