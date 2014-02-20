# Remove python byte-code compile step
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

Name:           fetch-ban
Version:        1.0.0
Release:        2%{?dist}
Summary:        A tool for creating ban_users.db from remote servers
Group:          Applications/Internet
License:        GPLv3
URL:            https://github.com/sfayer/fetch-ban
Source0:        https://raw2.github.com/sfayer/fetch-ban/master/fetch-ban.py
Source1:        https://raw2.github.com/sfayer/fetch-ban/master/fetch-ban.cron
Source2:        https://raw2.github.com/sfayer/fetch-ban/master/README.bans
BuildArch:      noarch
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Requires:       vixie-cron python python-pycurl

%description
Fetch-ban is a cron job for downloading remote DN ban lists to output a single
ban_users.db file.

%prep

%build

%install
rm -Rf %{buildroot}
# Install binary
mkdir -p %{buildroot}%{_bindir}
cp %{SOURCE0} %{buildroot}%{_bindir}/fetch-ban.py
chmod 755 %{buildroot}%{_bindir}/fetch-ban.py
# Install cron job
mkdir -p %{buildroot}%{_sysconfdir}/cron.d
cp %{SOURCE1} %{buildroot}%{_sysconfdir}/cron.d/fetch-ban.cron
# We also need the lcas dir (for output)
mkdir -p %{buildroot}%{_sysconfdir}/lcas
touch %{buildroot}%{_sysconfdir}/lcas/ban_static.db
cp %{SOURCE2} %{buildroot}%{_sysconfdir}/lcas/README

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%attr(644, -, -) %{_sysconfdir}/cron.d/fetch-ban.cron
%attr(755, -, -) %{_bindir}/fetch-ban.py
%config(noreplace) %{_sysconfdir}/lcas/ban_static.db
%doc %{_sysconfdir}/lcas/README

%changelog
* Thu Feb 20 2014 Simon Fayer <sf105@ic.ac.uk> - 1.0.0-2
- Added readme to hint to a sysadmin on how to ban a user.

* Tue Feb 18 2014 Simon Fayer <sf105@ic.ac.uk> - 1.0.0-1
- Initial release.

