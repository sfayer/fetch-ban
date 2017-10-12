%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

Name:           fetch-ban
Version:        2.0.1
Release:        1%{?dist}
Summary:        A tool for updating ban lists from remote servers
Group:          Applications/Internet
License:        GPLv3
URL:            https://github.com/sfayer/fetch-ban
Source0:        https://github.com/sfayer/fetch-ban/%{name}-%{version}.tar.bz2
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildArch:      noarch

BuildRequires:  python >= 2.6 python-devel
Requires:       python >= 2.6 python-pycurl

%description
Fetch-ban is a cron job for downloading remote DN ban lists to output various
local ban files.

%prep
%setup -q

%build
%{__python2} setup.py build

%install
rm -Rf %{buildroot}
%{__python2} setup.py install --skip-build --root %{buildroot}
# Cron
install -d %{buildroot}/%{_sysconfdir}/cron.d
install -m 0644 fetch-ban.cron \
                %{buildroot}/%{_sysconfdir}/cron.d/fetch-ban.cron
# Conf
install -d %{buildroot}/%{_sysconfdir}
install -m 0600 fetch-ban.conf %{buildroot}/%{_sysconfdir}/fetch-ban.conf
touch fetch-ban.bans
install -m 0600 fetch-ban.bans %{buildroot}/%{_sysconfdir}/fetch-ban.bans
# Working dir
install -m 0700 -d %{buildroot}/%{_sharedstatedir}/%{name}

%clean
rm -Rf %{buildroot}

%files
%defattr(-,root,root,-)
%attr(644, root, root) %doc README
%attr(755, root, root) %{_bindir}/fetch-ban
%attr(755, root, root) %dir %{python2_sitelib}/FetchBanLib
%attr(755, root, root) %{python2_sitelib}/FetchBanLib/*.py*
%attr(600, root, root) %config(noreplace)%{_sysconfdir}/cron.d/fetch-ban.cron
%attr(600, root, root) %config(noreplace) %{_sysconfdir}/fetch-ban.conf
%attr(600, root, root) %config(noreplace) %{_sysconfdir}/fetch-ban.bans
%attr(755, root, root) %{python2_sitelib}/fetch_ban-%{version}-py2.*.egg-info
%attr(700, root, root) %dir %{_sharedstatedir}/%{name}

%changelog
* Thu Oct 12 2017 Simon Fayer <sf105@ic.ac.uk> - 2.0.1-1
- Adjust dCache module for newer versions.

* Thu Dec 11 2014 Simon Fayer <sf105@ic.ac.uk> - 2.0.0-3
- Minor bug fixes for problems found in testing. New plugins.

* Thu Dec 11 2014 Simon Fayer <sf105@ic.ac.uk> - 2.0.0-2
- Include empty fetch-ban.bans file by default.

* Tue Dec 09 2014 Simon Fayer <sf105@ic.ac.uk> - 2.0.0-1
- New fetch-ban2 release with plugin support and many other improvements.

* Thu Feb 20 2014 Simon Fayer <sf105@ic.ac.uk> - 1.0.0-2
- Added readme to hint to a sysadmin on how to ban a user.

* Tue Feb 18 2014 Simon Fayer <sf105@ic.ac.uk> - 1.0.0-1
- Initial release.

