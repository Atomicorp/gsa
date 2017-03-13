Summary: GSA
Name:    greenbone-security-assistant
Version: 7.0.2
Release: 24%{?dist}.art
Source0: http://wald.intevation.org/frs/download.php/2429/greenbone-security-assistant-7.0.2.tar.gz
Source1: gsad.sysconfig
Source2: gsad.logrotate
Source3: gsad.init
Source4: gsad.service
Patch0: gsad-8.0.1-werror.patch
License: GNU GPLv2
URL: http://www.openvas.org
Group: System Environment/Libraries
Vendor: OpenVAS Development Team, http://www.openvas.org
Packager: Scott R. Shinn <scott@atomicorp.com>
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Prefix: %{_prefix}
Provides: openvas-gsa


BuildRequires: openvas-libraries-devel >= 7.0
BuildRequires: flex 
BuildRequires: automake  libtool 
BuildRequires:  cmake >= 2.6.0
BuildRequires: libgcrypt-devel gpgme gpgme-devel
BuildRequires: libmicrohttpd libmicrohttpd-devel libxml2 libxml2-devel
BuildRequires: doxygen
BuildRequires: openvas-smb

Requires: libmicrohttpd
Requires: openvas-scanner, openvas-manager

BuildRequires: libxslt libxslt-devel
%if 0%{?rhel} >= 7 || 0%{?fedora} > 15
BuildRequires:  systemd
Requires(post): systemd
Requires(preun):        systemd
Requires(postun):       systemd
%else
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
%endif

Requires: openvas-libraries  >= 3.0
Requires: logrotate


%if 0%{?fedora} >= 12 || 0%{?rhel} >= 6
BuildRequires: libuuid libuuid-devel
%else
BuildRequires: e2fsprogs e2fsprogs-devel
%endif


# OV-7
%if  0%{?rhel} == 6
BuildRequires: atomic-gnutls3-gnutls-devel
BuildRequires: atomic-glib2-glib2-devel
BuildRequires: atomic-libxslt-libxslt-devel

BuildConflicts: gnutls gnutls-devel
Requires: atomic-gnutls3-gnutls atomic-glib2-glib2 atomic-libxslt-libxslt
%else
BuildRequires: gnutls-devel
BuildRequires: glib2 >= 2.6.0, glib2-devel >= 2.6.0, 
%endif

BuildRequires: libpcap-devel

 
%description
GSA

%prep
%setup -n %{name}-%{version} -b 0
%patch0 -p1 

%build

%if 0%{?rhel} == 6
  export CC="gcc -Wl,-rpath,/opt/atomic/atomic-gnutls3/root/usr/lib,-rpath,/opt/atomic/atomic-gnutls3/root/usr/lib64,-rpath,/opt/atomic/atomic-glib2/root/usr/lib64/,-rpath,/opt/atomic/atomic-glib2/root/usr/lib/"
  export LDFLAGS="-L/opt/atomic/atomic-gnutls3/root/usr/lib -L/opt/atomic/atomic-gnutls3/root/usr/lib64 -L/lib -L/usr/openvas/lib/ -L/usr/openvas/lib64/"
  export CFLAGS="-I/opt/atomic/atomic-gnutls3/root/usr/include  -I/usr/openvas/include"
  export GNUTLS_LIBS=/opt/atomic/atomic-gnutls3/root/usr/lib:/opt/atomic/atomic-gnutls3/root/usr/lib64
  export PKG_CONFIG_PATH=/opt/atomic/atomic-glib2/root/usr/lib64/pkgconfig:/opt/atomic/atomic-gnutls3/root/usr/lib/pkgconfig:/opt/atomic/atomic-gnutls3/root/usr/lib64/pkgconfig:/usr/lib/pkgconfig/
%endif

export CFLAGS="$RPM_OPT_FLAGS -Werror=unused-but-set-variable -lgpg-error -Wno-error=deprecated-declarations"

%cmake -DLOCALSTATEDIR:PATH=%{_var} -DSYSCONFDIR:PATH=/etc/
#make %{?_smp_mflags} VERBOSE=1
make VERBOSE=1

#cmake -DCMAKE_VERBOSE_MAKEFILE=ON \
#        -DCMAKE_INSTALL_PREFIX=%{_prefix} \
#        -DSYSCONFDIR=%{_sysconfdir} \
#        -DLOCALSTATEDIR=%{_localstatedir}

#%{__make}  %{?_smp_mflags}
#%{__make}  
#%{__make}  doc


%install
rm -rf %{buildroot}
%{__make} install DESTDIR=%{buildroot}

%{__install} -D -m 644 %{SOURCE1} %{buildroot}/%{_sysconfdir}/sysconfig/gsad
%{__install} -D -m 644 %{SOURCE2} %{buildroot}/%{_sysconfdir}/logrotate.d/gsad

%if 0%{?rhel} >= 7 || 0%{?fedora} > 15
%{__install} -Dp -m 644 %{SOURCE4} %{buildroot}/%{_unitdir}/gsad.service
%else
%{__install} -D -m 755 %{SOURCE3} %{buildroot}/%{_sysconfdir}/init.d/gsad
%endif

%{__mkdir_p}  %{buildroot}%{_localstatedir}/log/openvas
touch %{buildroot}%{_localstatedir}/log/openvas/gsad.log


%clean
rm -rf $RPM_BUILD_ROOT

%if 0%{?rhel} >= 7 || 0%{?fedora} > 15

%post
%systemd_post gsad.service

%preun
%systemd_preun gsad.service

%postun
%systemd_postun_with_restart gsad.service


%else


%post 
if [ $1 = 1 ]; then
        /sbin/chkconfig --add gsad
fi

%preun
if [ $1 = 0 ]; then
    /sbin/service gsad stop > /dev/null 2>&1 || :
    /sbin/chkconfig --del gsad
fi

%postun
if [ $1 = 1 ]; then
    /sbin/service gsad condrestart
fi

%endif



%files
%defattr(-,root,root,-)
%doc CHANGES ChangeLog COPYING README
%config(noreplace) /etc/sysconfig/gsad
%config(noreplace) %{_sysconfdir}/openvas/gsad_log.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/gsad
%{_sbindir}/gsad
%{_mandir}/man8/gsad.8*
%if 0%{?rhel} >= 7 || 0%{?fedora} > 15
%{_unitdir}/gsad.service
%else
/etc/init.d/gsad
%endif
/usr/share/openvas/gsa
%dir %{_localstatedir}/log/openvas
%ghost %{_localstatedir}/log/openvas/gsad.log



%changelog
* Wed Feb 3 2016 Scott R. Shinn <scott@atomicorp.com> - 6.0.9-24
- Update to 6.0.9

* Wed Jan 13 2016 Scott R. Shinn <scott@atomicorp.com> - 6.0.8-23
- Update to 6.0.8

* Tue Dec 22 2015 Scott R. Shinn <scott@atomicorp.com> - 6.0.7-22
- Update to 6.0.7

* Sat Oct 10 2015 Scott R. Shinn <scott@atomicorp.com> - 6.0.6-21
- Update to 6.0.6

* Mon Aug 3 2015 Scott R. Shinn <scott@atomicorp.com> - 6.0.5-20
- Update to 6.0.5

* Mon Jul 13 2015 Scott R. Shinn <scott@atomicorp.com> - 6.0.4-19
- Update to 6.0.4

* Wed Jun 3 2015 Scott R. Shinn <scott@atomicorp.com> - 6.0.3-18
- Updates for systemd support

* Thu May 28 2015 Scott R. Shinn <scott@atomicorp.com> - 6.0.3-17
- Update to 6.0.3

* Wed Mar 18 2015 Scott R. Shinn <scott@atomicorp.com> - 5.0.6-16
- Update to 5.0.6

* Fri Jan 30 2015 Scott R. Shinn <scott@atomicorp.com> - 5.0.5-15
- Update to 5.0.5

* Mon Nov 17 2014 Scott R. Shinn <scott@atomicorp.com> - 5.0.4-14
- Update to 5.0.4

* Tue Sep 9 2014 Scott R. Shinn <scott@atomicorp.com> - 5.0.3-13
- Update to 5.0.3

* Fri Aug 1 2014 Scott R. Shinn <scott@atomicorp.com> - 5.0.2-12
- Update to 5.0.2

* Thu Jun 19 2014 Scott R. Shinn <scott@atomicorp.com> - 5.0.1-11
- Add -rpath for EL6 builds

* Mon Jun 16 2014 Scott R. Shinn <scott@atomicorp.com> - 5.0.1-9
- Update to 5.0.1
- Add logic for el6

* Mon Jun 9 2014 Scott R. Shinn <scott@atomicorp.com> - 5.0.0-8
- Bugfix for init scripts

* Mon May 5 2014 Scott R. Shinn <scott@atomicorp.com> - 5.0.0-7
- Update to 5.0.0

* Fri Oct 25 2013 Scott R. Shinn <scott@atomicorp.com> - 4.0.2-6
- Update to 4.0.2

* Fri Jun 7 2013 Scott R. Shinn <scott@atomicorp.com> - 4.0.1-5
- Update to 4.0.1

* Thu Apr 18 2013 Scott R. Shinn <scott@atomicorp.com> - 4.0.0-4
- Update to 4.0.0

* Mon Aug 20 2012 Scott R. Shinn <scott@atomicorp.com> - 3.0.3-3
- Update to 3.0.3

* Thu May 10 2012 Scott R. Shinn <scott@atomicorp.com> - 3.0.1-2
- Update to 3.0.1

* Tue Apr 24 2012 Scott R. Shinn <scott@atomicorp.com> - 3.0.0-1
- Update to 3.0.0

* Wed Aug 31 2011 Scott R. Shinn <scott@atomicorp.com> - 2.0.1-4
- Rebuild against newer libmicrohttpd

* Thu Mar 17 2011 Scott R. Shinn <scott@atomicorp.com> - 2.0.1-1
- Update to 2.0.1-1

* Tue Feb 22 2011 Scott R. Shinn <scott@atomicorp.com> - 2.0.0-1
- Update to 2.0.0-1

* Thu Feb 17 2011 Scott R. Shinn <scott@atomicorp.com> - 2.0-0.4
- Update to 2.0rc4

* Tue Feb 1 2011 Scott R. Shinn <scott@atomicorp.com> - 2.0-0.2
- Update to 2.0rc2

* Mon Aug 30 2010 Scott R. Shinn <scott@atomicorp.com> - 1.0.2-1
- Update to 1.0.2

* Mon Aug 2 2010 Scott R. Shinn <scott@atomicorp.com> - 1.0.0-0.1
- Initial build
