#Module-Specific definitions
%define mod_name mod_authz_ldap
%define mod_conf A31_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	LDAP authorization module for apache
Name:		apache-%{mod_name}
Version:	0.28
Release:	6
Group:		System/Servers
License:	GPL
URL:		http://authzldap.othello.ch/
Source0:	%{mod_name}-%{version}.tar.gz
Source1:	%{mod_conf}
BuildRequires:	openssl-devel
BuildRequires:	openldap-devel
BuildRequires:	automake
BuildRequires:	autoconf2.5
Requires:	openldap
Requires:	apache-mod_ssl
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
Epoch:		1

%description
The mod_authz_ldap package provides support for authenticating
users of the Apache HTTP server against an LDAP database.
mod_authz_ldap features the ability to authenticate users based on
the SSL client certificate presented, and also supports password
aging, and authentication based on role or by configured filters.

%prep

%setup -q -n %{mod_name}-%{version}

cp %{SOURCE1} %{mod_conf}

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
#export WANT_AUTOCONF_2_5=1
#rm -f configure
#libtoolize --copy --force; aclocal; autoconf --force; autoheader; automake --add-missing

export CPPFLAGS="`apr-1-config --includes` `apu-1-config --includes` -I%{_includedir}/openssl -DLDAP_DEPRECATED=1"

%configure2_5x --localstatedir=/var/lib \
    --with-apxs=%{_bindir}/apxs \
    --disable-static

pushd module
%{_bindir}/apxs -Wl,-export-symbols-regex -Wl,authz_ldap_module \
    -Wc,-DAUTHZ_LDAP_HAVE_SSL -c -o mod_authz_ldap.la *.c \
    -DAUTHZ_LDAP_HAVE_SSL -Wl,-lldap -Wl,-lcrypto
popd

%make -C tools

%install

make -C tools install DESTDIR=%{buildroot}
make -C docs install DESTDIR=%{buildroot}

# fix advx compat
rm -rf .libs; cp -rp module/.libs .

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean

%files
%doc ldap/*.schema docs/*.{html,jpg} docs/*.{HOWTO,txt} docs/README
%doc NEWS AUTHORS ChangeLog COPYING INSTALL
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%attr(0755,root,root) %{_bindir}/cert*
%attr(0644,root,root) %{_mandir}/man1/cert*


%changelog
* Sat Feb 11 2012 Oden Eriksson <oeriksson@mandriva.com> 1:0.28-5mdv2012.0
+ Revision: 772593
- rebuild

* Tue May 24 2011 Oden Eriksson <oeriksson@mandriva.com> 1:0.28-4
+ Revision: 678279
- mass rebuild

* Mon Jan 03 2011 Oden Eriksson <oeriksson@mandriva.com> 1:0.28-3mdv2011.0
+ Revision: 627726
- don't force the usage of automake1.7

* Sun Oct 24 2010 Oden Eriksson <oeriksson@mandriva.com> 1:0.28-2mdv2011.0
+ Revision: 587937
- rebuild

* Sun Oct 24 2010 Oden Eriksson <oeriksson@mandriva.com> 1:0.28-1mdv2011.0
+ Revision: 587902
- 0.28
- drop all patches

* Fri Apr 23 2010 Funda Wang <fwang@mandriva.org> 1:0.26-16mdv2010.1
+ Revision: 538086
- rebuild

* Mon Mar 08 2010 Oden Eriksson <oeriksson@mandriva.com> 1:0.26-15mdv2010.1
+ Revision: 516065
- rebuilt for apache-2.2.15

* Sat Aug 01 2009 Oden Eriksson <oeriksson@mandriva.com> 1:0.26-14mdv2010.0
+ Revision: 406548
- rebuild

* Sun Jun 28 2009 Oden Eriksson <oeriksson@mandriva.com> 1:0.26-13mdv2010.0
+ Revision: 390218
- sync with redhat

* Sun Mar 22 2009 Oden Eriksson <oeriksson@mandriva.com> 1:0.26-12mdv2009.1
+ Revision: 360285
- sync with fedora

* Tue Jan 06 2009 Oden Eriksson <oeriksson@mandriva.com> 1:0.26-11mdv2009.1
+ Revision: 325576
- rebuild

* Mon Jul 14 2008 Oden Eriksson <oeriksson@mandriva.com> 1:0.26-10mdv2009.0
+ Revision: 234734
- rebuild

* Thu Jun 05 2008 Oden Eriksson <oeriksson@mandriva.com> 1:0.26-9mdv2009.0
+ Revision: 215545
- fix rebuild
- hard code %%{_localstatedir}/lib to ease backports

* Fri Mar 07 2008 Oden Eriksson <oeriksson@mandriva.com> 1:0.26-8mdv2008.1
+ Revision: 181690
- rebuild

* Thu Dec 20 2007 Olivier Blin <blino@mandriva.org> 1:0.26-7mdv2008.1
+ Revision: 135820
- restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sat Sep 08 2007 Oden Eriksson <oeriksson@mandriva.com> 1:0.26-7mdv2008.0
+ Revision: 82532
- rebuild

* Sat Aug 18 2007 Oden Eriksson <oeriksson@mandriva.com> 1:0.26-6mdv2008.0
+ Revision: 65628
- rebuild


* Sun Mar 11 2007 Oden Eriksson <oeriksson@mandriva.com> 0.26-5mdv2007.1
+ Revision: 141275
- rebuild
- rebuild

* Thu Nov 09 2006 Oden Eriksson <oeriksson@mandriva.com> 1:0.26-3mdv2007.1
+ Revision: 79349
- Import apache-mod_authz_ldap

* Mon Aug 07 2006 Oden Eriksson <oeriksson@mandriva.com> 1:0.26-3mdv2007.0
- rebuild

* Mon Nov 28 2005 Oden Eriksson <oeriksson@mandriva.com> 1:0.26-2mdk
- sync with fedora (0.26-6)

* Mon Nov 28 2005 Oden Eriksson <oeriksson@mandriva.com> 1:0.26-1mdk
- fix versioning

* Wed Aug 31 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54_0.26-3mdk
- rebuilt against new openldap-2.3.6 libs

* Sun Jul 31 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54_0.26-2mdk
- fix deps

* Fri Jun 03 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54_0.26-1mdk
- rename the package
- the conf.d directory is renamed to modules.d
- use new rpm-4.4.x pre,post magic

* Sun Mar 20 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_0.26-4mdk
- use the %1

* Mon Feb 28 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_0.26-3mdk
- fix %%post and %%postun to prevent double restarts
- fix bug #6574

* Wed Feb 16 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_0.26-2mdk
- spec file cleanups, remove the ADVX-build stuff

* Tue Feb 08 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_0.26-1mdk
- rebuilt for apache 2.0.53

* Mon Feb 07 2005 Buchan Milne <bgmilne@linux-mandrake.com> 2.0.52_0.26-2mdk
- rebuild for ldap2.2_7

* Fri Nov 26 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.52_0.26-1mdk
- initial fedora import

