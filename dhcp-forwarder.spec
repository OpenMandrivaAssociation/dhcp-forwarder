# OE: conditional switches
#
#(ie. use with rpm --rebuild):
#
#      --with diet     Compile dhcp-forwarder against dietlibc

%define build_diet 0

# commandline overrides:
# rpm -ba|--rebuild --with 'xxx'
%{?_with_diet: %{expand: %%define build_diet 1}}

%define name dhcp-forwarder
%define version 0.8
%define release %mkrel 2

Summary:	An DHCP relay agent
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	GPL
Group:		System/Servers
URL:		http://www.nongnu.org/dhcp-fwd/
Source0:	%{name}-%{version}.tar.bz2
Source1:	dhcp-fwd.init.bz2
BuildRoot:	%{_tmppath}/%{name}-%{version}-root
Conflicts:	dhcpd-relay
Requires(pre):		rpm-helper
Requires(post):		rpm-helper
Requires(preun):	rpm-helper
Requires(postun):   rpm-helper

%if %{build_diet}
BuildRequires:	dietlibc-devel >= 0.20-1mdk
%endif

%description
dhcp-fwd forwards DHCP messages between subnets with different sublayer
broadcast domains. It is similar to the DHCP relay agent dhcrelay of
ISC's DHCP, but has the following features which are important for me:

* Runs as non-root in a chroot-jail
* Uses "normal" AF_INET sockets which allows to uses packagefilters to
  filter incoming messages.
* The DHCP agent IDs can be defined freely
* Has a small memory footprint when using dietlibc

%prep

%setup -q
bzcat %SOURCE1 > dhcp-fwd.init

%build

%if %{build_diet}
%configure --enable-release enable-dietlibc
make CC="diet gcc" CFLAGS="-Os -s -static -nostdinc"
%else
%configure --enable-release --disable-dietlibc
%make
%endif

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

make DESTDIR=%{buildroot} install
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sysconfdir}/sysconfig

install -m755 dhcp-fwd.init %{buildroot}%{_initrddir}/dhcp-fwd
install -m644 contrib/dhcp-fwd.conf %{buildroot}%{_sysconfdir}/dhcp-fwd.conf
install -m644 contrib/dhcp-fwd.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/dhcp-fwd

install -m755 -d %{buildroot}/var/lib/dhcpfwd

%pre
%_pre_useradd dhcp-fwd /var/lib/dhcpfwd /bin/false

%post
%_post_service dhcp-fwd

%preun
%_preun_service dhcp-fwd

%postun
%_postun_userdel dhcp-fwd

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog NEWS README
%config(noreplace) %{_initrddir}/dhcp-fwd
%config(noreplace) %{_sysconfdir}/sysconfig/dhcp-fwd
%config(noreplace) %{_sysconfdir}/dhcp-fwd.conf
%{_sbindir}/*
%dir /var/lib/dhcpfwd
%{_mandir}/man1/*


