#Module-Specific definitions
%define mod_name mod_authz_ldap
%define mod_conf A31_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	LDAP authorization module for apache
Name:		apache-%{mod_name}
Version:	0.28
Release:	%mkrel 4
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
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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
    --with-apxs=%{_sbindir}/apxs \
    --disable-static

pushd module
%{_sbindir}/apxs -Wl,-export-symbols-regex -Wl,authz_ldap_module \
    -Wc,-DAUTHZ_LDAP_HAVE_SSL -c -o mod_authz_ldap.la *.c \
    -DAUTHZ_LDAP_HAVE_SSL -Wl,-lldap -Wl,-lcrypto
popd

%make -C tools

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

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
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc ldap/*.schema docs/*.{html,jpg} docs/*.{HOWTO,txt} docs/README
%doc NEWS AUTHORS ChangeLog COPYING INSTALL
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%attr(0755,root,root) %{_bindir}/cert*
%attr(0644,root,root) %{_mandir}/man1/cert*
