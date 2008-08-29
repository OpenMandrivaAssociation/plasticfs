%define major	0
%define libname		%mklibname %{name} %{major}
%define develname	%mklibname %{name} -d

%define build_debug	0
%define build_paranoid	0

%{expand: %{?_with_debug: 	%%global build_debug 1}}
%{expand: %{?_with_paranoid: 	%%global build_paranoid 1}}
%{expand: %{?_without_paranoid:	%%global build_paranoid 0}}

Name:		plasticfs
Version:	1.11
Release:	%{mkrel 1}
Summary:	An user-space virtual filesystem implementation
License:	GPLv3+
Group:		File tools
URL:		http://plasticfs.sourceforge.net/
Source0:	http://plasticfs.sourceforge.net/%{name}-%{version}.tar.gz
Patch0:		plasticfs-1.11-non-paranoid.patch
Patch1:		plasticfs-1.11-dlsym-debug.patch
Patch2:		plasticfs-1.11-makefile.patch
BuildRequires:  groff
BuildRequires:  libtool
BuildRoot:	%{_tmppath}/%{name}-root

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
Libraries for the Plastic File System.

%package -n %{develname}
Summary:	Development libraries for the Plastic File System
Group:		Development/C
Provides:	%{name}-devel
Requires:	%{libname} = %{version}
Obsoletes:	%{mklibname plasticfs 0 -d}

%description -n %{develname}
Development libraries for the Plastic File System.

%define _requires_exceptions libc.so.6(GLIBC_PRIVATE)

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
EXTRA_FLAGS="-DNOT_IN_libc"
%if !%{build_paranoid}
	EXTRA_FLAGS="$EXTRA_FLAGS -DNON_PARANOID"
%endif
%if %{build_debug}
	EXTRA_FLAGS="$EXTRA_FLAGS -DVIEWPATH_DEBUG -DDLSYM_DEBUG -DFILTER_DEBUG"
%endif
%configure CXXFLAGS="$EXTRA_FLAGS"
sed -i -e 's/libtool/libtool --tag=cxx/g' Makefile
# (misc) here because we patch the makefile directly
%make 

%install
rm -rf %{buildroot}
%makeinstall_std

# convenience function
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/plasticfs << EOF
#!/bin/sh
if [ -z "\$1" ]; then
	echo "USAGE: plasticfs <command>"
	exit 1
fi

if [ -n "\$PLASTICFS" ]; then
	LD_PRELOAD="%{_libdir}/libplasticfs.so.%{major} \$LD_PRELOAD" \\
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

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif
%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%files
%defattr(-,root,root)
%doc BUILDING README
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
%{_libdir}/libplasticfs.so.%{major}*

%files -n %{develname}
%defattr(-,root,root)
%{_libdir}/libplasticfs.*a
%{_libdir}/libplasticfs.so

