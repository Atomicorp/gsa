Summary: GSA
Name:    greenbone-security-assistant
Version: 8.0.0
Release: RELEASE-AUTO%{?dist}.art
Source0:        https://github.com/greenbone/gsa/archive/v%{version}.tar.gz
Source1: gsad.sysconfig
Source2: gsad.logrotate
Source3: gsad.init
Source4: gsad.service
Patch1: openvas-gsa-pki.patch
Patch2: openvas-gsa-gsad_js-fr.patch
Patch3: openvas-gsa-polib.patch
Patch4: openvas-gsa-doxygen_full.patch
Patch5: openvas-gsa-strncpy.patch


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

# El7
%if  0%{?rhel} == 7
BuildRequires: atomic-libgcrypt, atomic-libgcrypt-devel
BuildRequires: atomic-libgpg-error, atomic-libgpg-error-devel
BuildRequires: atomic-gpgme, atomic-gpgme-devel
BuildRequires: atomic-zlib, atomic-zlib-devel
BuildRequires: cmake3
BuildRequires: rh-nodejs8

%else
BuildRequires: libgcrypt-devel
BuildRequires: nodejs
BuildRequires: npm
%endif

# new requires
#BuildRequires: yarn

BuildRequires: gpgme gpgme-devel
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
The Greenbone Security Assistant (GSA) is a lean web service offering a user
web interface for the Open Vulnerability Assessment System (OpenVAS).
The GSA uses XSL transformation style-sheets that converts OMP responses
from the OpenVAS infrastructure into presentable HTML.


%package doc
Summary:        Development documentation for %{name}
BuildRequires:  graphviz

%description doc
You can find documentation for development of %{name} under file://%{_docdir}/%{name}-doc.
It can be used with a Browser.


%prep
%setup -q -n gsa-%{version}


%build

export CFLAGS="$RPM_OPT_FLAGS -Werror=unused-but-set-variable -Wno-error=deprecated-declarations"

%if  0%{?rhel} == 7

        export CC="gcc -Wl,-rpath,/opt/atomicorp/atomic/root/usr/lib64/"
        export PATH="/opt/atomicorp/atomic/root/usr/bin:$PATH"
        export LDFLAGS="-L/opt/atomicorp/atomic/root/usr/lib64/ -lgcrypt -ldl -lgpg-error"
        export CFLAGS="$CFLAGS -I/opt/atomicorp/atomic/root/usr/include/"
        export PKG_CONFIG_PATH="/opt/atomicorp/atomic/root/usr/lib64/pkgconfig"
        export CMAKE_PREFIX_PATH="/opt/atomicorp/atomic/root/"

	source /opt/rh/rh-nodejs8/enable 


%endif


%if  0%{?rhel} == 7
cmake3 \
%else
%cmake \
%endif
	-DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_VERBOSE_MAKEFILE=ON \
        -DCMAKE_INSTALL_PREFIX=%{_prefix} \
        -DSYSCONFDIR=%{_sysconfdir} \
        -DLIBDIR=%{_libdir} \
        -DLOCALSTATEDIR=%{_localstatedir} 

make %{?_smp_mflags} VERBOSE=1
make doc-full


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

#find_lang gsad_xsl


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



#%files -f gsad_xsl.lang
%files 
%defattr(-,root,root,-)
%license LICENSE
%config(noreplace) /etc/sysconfig/gsad
%config(noreplace) /etc/gvm/gsad_log.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/gsad
%{_sbindir}/gsad
%{_mandir}/man8/gsad.8*
%if 0%{?rhel} >= 7 || 0%{?fedora} > 15
%{_unitdir}/gsad.service
%else
/etc/init.d/gsad
%endif
%dir %{_localstatedir}/log/openvas
%ghost %{_localstatedir}/log/openvas/gsad.log
/usr/share/gvm/*

%files doc
#%doc doc/generated/html/*



%changelog
* Sun Apr 7 2019 Scott R. Shinn <scott@atomicorp.com> - 8.0.0-RELEASE-AUTO
- Update to 8.0.0

* Wed Apr 3 2019 Scott R. Shinn <scott@atomicorp.com> - 7.0.3-RELEASE-AUTO
- Update to 7.0.3
- Merge elements from Fedora project

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
