Name:           fetch-ban
Version:        3.0.0
Release:        1%{?dist}
Summary:        A tool for updating ban lists from remote servers
Group:          Applications/Internet
License:        GPLv3
URL:            https://github.com/sfayer/fetch-ban
Source0:        https://github.com/sfayer/fetch-ban/%{name}-%{version}.tar.bz2
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildArch:      noarch

BuildRequires:  python3 >= 3.6 python3-devel python3-setuptools
Requires:       python3 >= 3.6 python3-pycurl

%description
Fetch-ban is a cron job for downloading remote DN ban lists to output various
local ban files.

%prep
%setup -q

%build
%{__python3} setup.py build

%install
rm -Rf %{buildroot}
%{__python3} setup.py install --skip-build --root %{buildroot}
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
%attr(755, root, root) %dir %{python3_sitelib}/FetchBanLib
%attr(755, root, root) %{python3_sitelib}/FetchBanLib/*.py*
%attr(755, root, root) %{python3_sitelib}/FetchBanLib/__pycache__/*.pyc
%attr(600, root, root) %config(noreplace)%{_sysconfdir}/cron.d/fetch-ban.cron
%attr(600, root, root) %config(noreplace) %{_sysconfdir}/fetch-ban.conf
%attr(600, root, root) %config(noreplace) %{_sysconfdir}/fetch-ban.bans
%attr(755, root, root) %{python3_sitelib}/fetch_ban-%{version}-py3.*.egg-info
%attr(700, root, root) %dir %{_sharedstatedir}/%{name}

%changelog
* Thu Nov 16 2023 Simon Fayer <sf105@ic.ac.uk> - 3.0.0-1
- Switch to python3

* Fri Feb 15 2019 Simon Fayer <sf105@ic.ac.uk> - 2.0.2-1
- Added new no_audit_re option to supress printing messages about some DNs.

* Fri Feb 08 2019 Simon Fayer <sf105@ic.ac.uk> - 2.0.1-2
- Add extra input source in example config for UK NGI ARGUS server.
- Make DN checking more permissive.

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

