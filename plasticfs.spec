%define name		plasticfs
%define version		1.9
%define release		%mkrel 3
%define libmajor	0
%define libname		%mklibname %{name} %{libmajor}
%define libname_devel	%mklibname %{name} %{libmajor} -d

%define build_debug	0
%define build_paranoid	0

%{expand: %{?_with_debug: 	%%global build_debug 1}}
%{expand: %{?_with_paranoid: 	%%global build_paranoid 1}}
%{expand: %{?_without_paranoid:	%%global build_paranoid 0}}

Name:		%{name}
Version:	%{version}
Release:	%{release}
Summary:	An user-space virtual filesystem implementation
License:	GPL
Group:		File tools
URL:		http://plasticfs.sourceforge.net/
Source0:	%{name}-%{version}.tar.bz2
Patch0:		%{name}-1.8-non-paranoid.patch.bz2
Patch1:		%{name}-1.8-dlsym-debug.patch.bz2
Requires:	%{libname} = %{version}
BuildRequires:  groff
BuildRequires:  libtool
%description
The Plastic File System is an LD_PRELOAD module for manipulating what
the file system looks like for programs. This allows virtual file
systems to exist in user space, without kernel hacks or modules.

A number of filters exist for a number of different use-cases, including
 
chroot    - simulate the effects of a chroot call
dos       - simulate a DOS 8.3 filesystem
downcase  - make file names appear in lower-case
log       - transparently log file system access (like strace)
nocase    - make filenames case-insensitive
shortname - simulate file systems with shorter filenames
smartlink - expand environment variables in symbolic links
titlecase - make filenames appear in title-case
upcase    - make filenames appear in upper-case
viewpath  - union all the directory trees in a view path (unionfs)

These filters may be piped on into the next to form powerful filter
combinations. 

It is possible to extend PlasticFS with loadable file system filter
modules from shared object files.
       
%package -n %{libname}
Summary:	Libraries for the Plastic File System
Group:		File tools
%description -n %{libname}
Libraries for the Plastic File System

%package -n %{libname_devel}
Summary:	Development libraries for the Plastic File System
Group:		Development/C
Provides:	lib%{name}-devel
Requires:	%{libname} = %{version}
%description -n %{libname_devel}
Development libraries for the Plastic File System

%define _requires_exceptions libc.so.6(GLIBC_PRIVATE)

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%build
EXTRA_FLAGS="-DNOT_IN_libc"
%if !%{build_paranoid}
	EXTRA_FLAGS="$EXTRA_FLAGS -DNON_PARANOID"
%endif
%if %{build_debug}
	EXTRA_FLAGS="$EXTRA_FLAGS -DVIEWPATH_DEBUG -DDLSYM_DEBUG -DFILTER_DEBUG"
%endif
%configure CXXFLAGS="$EXTRA_FLAGS"
perl -pi -e 's/libtool/libtool --tag=cxx/' Makefile
# (misc) here because we patch the makefile directly
%make 

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall_std

# convenience function
mkdir -p $RPM_BUILD_ROOT%{_bindir}
cat > $RPM_BUILD_ROOT%{_bindir}/plasticfs << EOF
#!/bin/sh
if [ -z "\$1" ]; then
	echo "USAGE: plasticfs <command>"
	exit 1
fi

if [ -n "\$PLASTICFS" ]; then
	LD_PRELOAD="%{_libdir}/libplasticfs.so.%{libmajor} \$LD_PRELOAD" \\
	PLASTICFS="\$PLASTICFS" \\
	\$@
else
	echo "ERROR: You need to specify the 'PLASTICFS' environment variable."
	echo "       See plasticfs(3) for details."
	exit 1
fi
EOF

%clean
rm -Rf %{buildroot}

%post -n %{libname} -p /sbin/ldconfig
%postun -n %{libname} -p /sbin/ldconfig

%files
%defattr(-,root,root)
%doc BUILDING README LICENSE
%attr(755,root,root) %{_bindir}/plasticfs
%{_mandir}/man1/plasticfs_license.1*
%{_mandir}/man3/plasticfs.3*
%{_mandir}/manl/plasticfs_chroot.l*
%{_mandir}/manl/plasticfs_dos.l*
%{_mandir}/manl/plasticfs_downcase.l*
%{_mandir}/manl/plasticfs_log.l*
%{_mandir}/manl/plasticfs_nocase.l*
%{_mandir}/manl/plasticfs_shortname.l*
%{_mandir}/manl/plasticfs_smartlink.l*
%{_mandir}/manl/plasticfs_titlecase.l*
%{_mandir}/manl/plasticfs_upcase.l*
%{_mandir}/manl/plasticfs_viewpath.l*

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/libplasticfs.so.%{libmajor}
%{_libdir}/libplasticfs.so.%{libmajor}.0.0

%files -n %{libname_devel}
%defattr(-,root,root)
%{_libdir}/libplasticfs.a
%{_libdir}/libplasticfs.la
%{_libdir}/libplasticfs.so

