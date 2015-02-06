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
Release:	3
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

%if %{_use_internal_dependency_generator}
%define __noautoreq 'libc.so.6\\(GLIBC_PRIVATE\\)'
%else
%define _requires_exceptions libc.so.6(GLIBC_PRIVATE)
%endif

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
%{_libdir}/libplasticfs.so



%changelog
* Sat Aug 30 2008 Adam Williamson <awilliamson@mandriva.com> 1.11-1mdv2009.0
+ Revision: 277516
- simply file lists
- don't package license
- %%{buildroot} not $RPM_BUILD_ROOT
- sed not perl
- add some newlines to improve readability
- add makefile.patch: restore lines apparently missing from end of makefile
  that break installation
- rediff non-paranoid.patch and dlsym-debug.patch
- new license policy
- new devel policy
- drop unnecessary defines
- new release 1.11

  + Thierry Vignaud <tvignaud@mandriva.com>
    - rebuild
    - kill re-definition of %%buildroot on Pixel's request

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - import plasticfs


* Tue Apr 25 2006 Nicolas Lécureuil <neoclust@mandriva.org> 1.9-3mdk
- Fix BuildRequires

* Tue Dec 27 2005 Michael Scherer <misc@mandriva.org> 1.9-2mdk
- Fix BuildRequires ( groff, for man pages )

* Thu Nov 10 2005 Michael Scherer <misc@mandriva.org> 1.9-1mdk
- new version 1.9
- mkrel
- rpmbuildupdate-aware
- remove patch2, applied upstream

* Wed Jun 30 2004 Michael Scherer <misc@mandrake.org> 1.8-2mdk 
- rebuild for new gcc 
- patch for new gcc and libtool ( patch 0 )
 
* Fri Jan 16 2004 Jaco Greeff <jaco@mandrake.org> 1.8-1mdk
- Version 1.8
- Add --with debug & paranoid options
- patch1: Fix compiler error with DLSYM_DEBUG defined

* Wed Jan 14 2004 Jaco Greeff <jaco@mandrake.org> 1.7-1mdk
- Initial MDK package, version 1.7
- patch0: Allow execution as root user
