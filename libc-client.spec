%define soname		c-client
%define somajver	2007
%define shlibname	lib%{soname}.so.%{somajver}

Summary: C-client mail access routines for IMAP and POP protocols
Name:	 libc-client
Version: 2007e
Release: 11%{?dist}

# See LICENSE.txt, http://www.apache.org/licenses/LICENSE-2.0
License: ASL 2.0 
Group: 	 System Environment/Daemons
URL:	 http://www.washington.edu/imap/
# Old (non-latest) releases live at  ftp://ftp.cac.washington.edu/imap/old/
Source0: ftp://ftp.cac.washington.edu/imap/imap-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Patch1: imap-2007-paths.patch
Patch5: imap-2007e-overflow.patch
Patch9: imap-2007e-shared.patch
Patch10: imap-2007e-authmd5.patch
BuildRequires: krb5-devel, openssl-devel, pam-devel

%description
C-client is a common API for accessing mailboxes. It is used internally by
the popular PINE mail reader, the University of Washington's IMAP server
and PHP.

%package devel
Summary: Development tools for programs which will use the IMAP library.
Group: Development/Libraries
Requires: libc-client = %{version}-%{release}

%description devel
The c-client-devel package contains the header files and static libraries
for developing programs which will use the C-client common API.

%prep
%setup -q -n imap-%{version}
chmod -R u+w .
%patch1 -p1 -b .paths

%patch5 -p1 -b .overflow

%patch9 -p1 -b .shared
%patch10 -p1 -b .authmd5


%build
# Kerberos setup
test -f %{_sysconfdir}/profile.d/krb5-devel.sh && source %{_sysconfdir}/profile.d/krb5-devel.sh
test -f %{_sysconfdir}/profile.d/krb5.sh && source %{_sysconfdir}/profile.d/krb5.sh
GSSDIR=$(krb5-config --prefix)

# SSL setup, probably legacy-only, but shouldn't hurt -- Rex
export EXTRACFLAGS="$EXTRACFLAGS $(pkg-config --cflags openssl 2>/dev/null)"
# $RPM_OPT_FLAGS
export EXTRACFLAGS="$EXTRACFLAGS -fPIC $RPM_OPT_FLAGS"
# jorton added these, I'll assume he knows what he's doing. :) -- Rex
export EXTRACFLAGS="$EXTRACFLAGS -fno-strict-aliasing"
%if 0%{?fedora} > 4 || 0%{?rhel} > 4
export EXTRACFLAGS="$EXTRACFLAGS -Wno-pointer-sign -Wno-parentheses"
%endif

echo -e "y\ny" | \
make %{?_smp_mflags} lnp \
IP=6 \
EXTRACFLAGS="$EXTRACFLAGS" \
EXTRALDFLAGS="$EXTRALDFLAGS" \
EXTRAAUTHENTICATORS=gss \
SPECIALS="GSSDIR=${GSSDIR} LOCKPGM=%{_sbindir}/mlock SSLCERTS=%{ssldir}/certs SSLDIR=%{ssldir} SSLINCLUDE=%{_includedir}/openssl SSLKEYS=%{ssldir}/private SSLLIB=%{_libdir}" \
SSLTYPE=unix \
CCLIENTLIB=$(pwd)/c-client/%{shlibname} \
SHLIBBASE=%{soname} \
SHLIBNAME=%{shlibname}
# Blank line

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_libdir}

install -m 755 ./c-client/%{shlibname} $RPM_BUILD_ROOT%{_libdir}/
ln -s %{shlibname} $RPM_BUILD_ROOT%{_libdir}/lib%{soname}.so

mkdir -p $RPM_BUILD_ROOT%{_includedir}/imap
install -m 644 ./c-client/*.h $RPM_BUILD_ROOT%{_includedir}/imap
# Added linkage.c to fix (#34658) <mharris>
install -m 644 ./c-client/linkage.c $RPM_BUILD_ROOT%{_includedir}/imap
install -m 644 ./src/osdep/tops-20/shortsym.h $RPM_BUILD_ROOT%{_includedir}/imap

#mkdir -p $RPM_BUILD_ROOT/%{_datadir}/ssl/certs

# don't ship quite so many docs
rm -rf docs/rfc docs/FAQ.txt

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}
touch $RPM_BUILD_ROOT%{_sysconfdir}/c-client.cf

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc LICENSE.txt NOTICE SUPPORT 
%doc docs/RELNOTES docs/*.txt
%ghost %config(missingok,noreplace) %{_sysconfdir}/c-client.cf
%{_libdir}/lib%{soname}.so.*

%files devel
%defattr(-,root,root)
%{_includedir}/imap
%{_libdir}/lib%{soname}.so

%changelog
* Wed May  5 2010 Joe Orton <jorton@redhat.com> - 2007e-11
- update to 2007e, merge with Fedora uw-imap spec (#586875)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2004g-2.2.1
- rebuild

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2004g-2.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2004g-2.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Tue Jan 31 2006 Joe Orton <jorton@redhat.com> 2004g-2
- bump soname (#179017)

* Thu Jan  5 2006 Jonathan Kamens <jik@kamens.brookline.ma.us> 2004g-1
- Upstream version 2004g (#176974)
- Remove obsolete doc file "WARNING"
- Remove security patch included in new upstream version
- Custom flock code no longer necessary; included in upstream

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Dec  1 2005 Nalin Dahyabhai <nalin@redhat.com> 2002e-18
- rebuild

* Thu Dec  1 2005 Nalin Dahyabhai <nalin@redhat.com> 2002e-17
- account for the /usr/share/ssl -> /etc/pki/tls move in the patch which
  sets the locations at compile-time (more of #165967)

* Wed Nov 23 2005 Nalin Dahyabhai <nalin@redhat.com> 2002e-16
- rebuild

* Wed Nov 23 2005 Nalin Dahyabhai <nalin@redhat.com> 2002e-15
- rebuild

* Wed Nov 23 2005 Nalin Dahyabhai <nalin@redhat.com> 2002e-14
- rebuild

* Wed Nov 23 2005 Nalin Dahyabhai <nalin@redhat.com> 2002e-13
- apply fix for CVE-2005-2933: buffer overflow (#171345)

* Wed Nov  9 2005 Tomas Mraz <tmraz@redhat.com> 2002e-12
- rebuilt against new openssl

* Sat Oct 15 2005 Florian La Roche <laroche@redhat.com>
- fix to rebuild at least, seems the way to specify the
  include dir is a bit broken

* Wed Mar  2 2005 Joe Orton <jorton@redhat.com> 2002e-10
- rebuild

* Wed Mar  2 2005 Jindrich Novy <jnovy@redhat.com> 2002e-9
- rebuilt

* Mon Sep 20 2004 Joe Orton <jorton@redhat.com> 2002e-8
- drop conflict with imap (#132928)

* Thu Aug 19 2004 Joe Orton <jorton@redhat.com> 2002e-7
- have -devel require libc-client of same VR

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Apr  7 2004 Joe Orton <jorton@redhat.com> 2002e-5
- rebuild

* Wed Apr 07 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 2002e-4
- Use CFLAGS (and RPM_OPT_FLAGS) during the compilation
- Build the .so through gcc instead of directly calling ld 

* Fri Mar  5 2004 Joe Orton <jorton@redhat.com> 2002e-3
- install .so with permissions 0755
- make auth_md5.c functions static to avoid symbol conflicts
- remove Epoch: 0

* Tue Mar 02 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:2002e-2
- "lnp" already uses RPM_OPT_FLAGS
- have us conflict with imap, imap-devel

* Tue Mar  2 2004 Joe Orton <jorton@redhat.com> 0:2002e-1
- add post/postun, always use -fPIC

* Tue Feb 24 2004 Kaj J. Niemi <kajtzu@fi.basen.net>
- Name change from c-client to libc-client

* Sat Feb 14 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:2002e-0.1
- c-client 2002e is based on imap-2002d
- Build shared version, build logic is copied from FreeBSD net/cclient

