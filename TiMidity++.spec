%define name	TiMidity++
%define version	2.13.2
%define release	32

# Stick to /usr/lib/timidity on any platform
# XXX probably better in /usr/share/timidity for arch independent data
# but it's not worth splitting that much
%define timiditydir	%{_prefix}/lib/timidity

#
# When big change is involved (e.g. timidity.cfg change location),
# so that new timidity binray and old patch RPM won't work together,
# increment this number by 1 for all timidity related RPMs
#
%define patch_pkg_version 2

#
# NOTE: When updating config for midia patch set, please refresh both
# config file included here and the one in patch pkg
#

Summary:	MIDI to WAVE converter and player
Name:		%{name}
Version:	%{version}
Release:	%{release}
URL:		http://timidity.sourceforge.net/
License:	GPLv2+
Group:		Sound
Source0:	%{name}-%{version}.tar.bz2
Source1:	http://www.timidity.jp/dist/cfg/timidity.cfg
Source2:	timidity-emacs-mode.el
Source3:	timidity.README.mdv
Source11:	%{name}48.png
Source12:	%{name}32.png
Source13:	%{name}16.png
# (Abel) change default config path to /etc/timidity/timidity.cfg
Patch0:		timidity-2.13.2-default-config-path.patch
# (Abel) it checked for speex.h, not speex/speex.h
Patch1:		timidity-2.13.2-speex-header-path.patch
# (Abel) fix timidity path in .el file and install .el file when
#        enabling dynamic module
Patch2:		timidity-2.13.2-emacs.patch
# (Abel) fix wishx path in tcl scripts
Patch3:		timidity-2.13.2-tcl.patch
# (Abel) CVS fixes for 2.13.2
Patch4:		timidity-2.13.2-cvs-fixes.patch
Patch5:		TiMidity++-2.13.2-gcc4.patch
#(nl) CVS Fix Build against portaudio V19
Patch6:         Timidity-fix-portaudioV19-build.diff
Patch7:		TiMidity++-2.13.2+flac-1.1.3-partial.patch
Patch8: timidity-2.13.2-tcl-legacy.patch
Patch9: timidity-2.13.2-wformat.patch
Requires:	timidity-instruments = %{patch_pkg_version}
BuildRequires:	pkgconfig(alsa)
BuildRequires:	autoconf
BuildRequires:	emacs-bin
BuildRequires:	esound-devel
BuildRequires:	gtk2-devel
BuildRequires:	jackit-devel
BuildRequires:	lesstif-devel
BuildRequires:	libao-devel
BuildRequires:	libflac-devel >= 1.1.3
BuildRequires:	liboggflac-devel
BuildRequires:	nas-devel
BuildRequires:	ncurses-devel
BuildRequires:	oggvorbis-devel
BuildRequires:	portaudio-devel
BuildRequires:	speex-devel
BuildRequires:	tcl-devel
BuildRequires:	tk-devel
BuildRequires:	libxaw-devel
BuildRequires:	slang-devel
BuildConflicts:	Xaw3d-devel


%description
TiMidity is a MIDI to WAVE converter and player that uses Gravis 
Ultrasound(tm) or SoundFont(tm) patch files to generate digital audio data
from general MIDI files. The audio data can be played through any 
sound device or stored on disk.

%package	interfaces-extra
Summary:	Extra GUI/text mode interfaces for TiMidity
Group:		Sound
Requires:	%{name} = %{version}-%{release}
Requires:	emacs-bin

%description	interfaces-extra
TiMidity is a MIDI to WAVE converter and player that uses Gravis 
Ultrasound(tm) or SoundFont(tm) patch files to generate digital audio data
from general MIDI files. The audio data can be played through any 
sound device or stored on disk.

Install this if you want to use TiMidity under other interfaces, such as
Motif(or Lesstif), Tcl/Tk, emacs etc.

%prep
%setup -q
%patch0 -p1 -b .default-path
%patch1 -p1 -b .speex-header
%patch2 -p1 -b .emacs
%patch3 -p1
%patch4 -p1 -b .cvs
%patch5 -p1 -b .gcc4
%patch6 -p0 -b .portaudioV19
%patch7 -p1 -b .flac
%patch8 -p0 -b .tcl_legacy
%patch9 -p0 -b .wformat

%build
autoconf

# little ugly trick to force install of tclIndex, running wish requires
# X display
touch interface/tclIndex



%configure2_5x \
	--enable-audio=oss,alsa,nas,esd,portaudio,jack,ao,vorbis,flac,speex \
	--enable-dynamic=dynamic,ncurses,slang,motif,tcltk,emacs,xaw,xskin,gtk \
	--enable-interface=alsaseq \
	--enable-network \
	--enable-server

%make LDFLAGS="-laudio -lFLAC"

%install
rm -rf %{buildroot}
%makeinstall_std
install -d %{buildroot}%{_datadir}/timidity
install -m644 %{SOURCE1} -D %{buildroot}%{_sysconfdir}/timidity/timidity-custom.cfg

install -d %{buildroot}%{_datadir}/applications
cat <<EOF > %{buildroot}%{_datadir}/applications/mandriva-%{name}.desktop
[Desktop Entry]
Name=TiMidity++
Comment=MIDI file player
Exec=timidity -ig
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=true
Categories=Audio;Midi;
EOF

#icons
install -m644 %{SOURCE11} -D %{buildroot}%{_iconsdir}/hicolor/48x48/apps/%{name}.png
install -m644 %{SOURCE12} -D %{buildroot}%{_iconsdir}/hicolor/32x32/apps/%{name}.png
install -m644 %{SOURCE13} -D %{buildroot}%{_iconsdir}/hicolor/16x16/apps/%{name}.png

# emacs mode
install -m644 %{SOURCE2} -D $RPM_BUILD_ROOT%{_sysconfdir}/emacs/site-start.d/timidity.el

# japanese manpages
install -m644 doc/ja_JP.eucJP/timidity.1 -D %{buildroot}%{_mandir}/ja/man1/timidity.1
install -m644 doc/ja_JP.eucJP/timidity.cfg.5 %{buildroot}%{_mandir}/ja/man1/timidity.cfg.5

%clean
rm -rf %{buildroot}

%post
%if %mdkversion < 200900
%update_menus
%update_icon_cache hicolor
%endif
%{_sbindir}/update-alternatives --install %{_sysconfdir}/timidity/timidity.cfg timidity.cfg %{_sysconfdir}/timidity/timidity-custom.cfg 10

%postun
%if %mdkversion < 200900
%clean_menus
%clean_icon_cache hicolor
%endif
if [ "$1" = "0" ]; then
%{_sbindir}/update-alternatives --remove timidity.cfg %{_sysconfdir}/timidity/timidity-custom.cfg
fi

%triggerpostun -- %{name} <= 2.13.2-22mdv
%{_sbindir}/update-alternatives --install %{_sysconfdir}/timidity/timidity.cfg timidity.cfg %{_sysconfdir}/timidity/timidity-custom.cfg 10

%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog INSTALL NEWS README doc/C/FAQ
%doc doc/C/README.{alsaseq,dl,sf,m2m,mts}
%config(noreplace) %{_sysconfdir}/timidity
%{_bindir}/timidity
%{_mandir}/man?/timidity*
%lang(ja) %{_mandir}/ja/man?/*
%{_datadir}/timidity
%dir %{timiditydir}
%{timiditydir}/interface_[gn].*
%{_datadir}/applications/mandriva-%{name}.desktop
%{_iconsdir}/hicolor/16x16/apps/%{name}.png
%{_iconsdir}/hicolor/32x32/apps/%{name}.png
%{_iconsdir}/hicolor/48x48/apps/%{name}.png

%files interfaces-extra
%defattr(-,root,root)
%doc doc/C/README.{tk,xaw,xskin}
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/*.el
%{timiditydir}/interface_[aeikms].*
%{_datadir}/emacs/site-lisp/*.el
%{timiditydir}/*.tcl
%{timiditydir}/tclIndex
%{timiditydir}/bitmaps


%changelog
* Fri Apr 15 2011 Antoine Ginies <aginies@mandriva.com> 2.13.2-30mdv2011.0
+ Revision: 653140
- bump the release

* Sun Mar 28 2010 Funda Wang <fwang@mandriva.org> 2.13.2-29mdv2010.1
+ Revision: 528353
- rebuild

* Tue Mar 16 2010 Oden Eriksson <oeriksson@mandriva.com> 2.13.2-28mdv2010.1
+ Revision: 521913
- rebuilt for 2010.1

* Sun Aug 09 2009 Oden Eriksson <oeriksson@mandriva.com> 2.13.2-27mdv2010.0
+ Revision: 413014
- rebuild

* Tue Mar 03 2009 Guillaume Rousse <guillomovitch@mandriva.org> 2.13.2-26mdv2009.1
+ Revision: 347818
- fix x86_64 build dependencies
- rebuild for latest tk libs

  + Götz Waschk <waschk@mandriva.org>
    - fix patch 9

  + Helio Chissini de Castro <helio@mandriva.com>
    - Adios arts
    - Fix TCL legacy build
    - Fix wformat errors

* Fri Jul 04 2008 Oden Eriksson <oeriksson@mandriva.com> 2.13.2-25mdv2009.0
+ Revision: 231808
- bump release
- fix build

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas

* Fri Jan 04 2008 Götz Waschk <waschk@mandriva.org> 2.13.2-23mdv2008.1
+ Revision: 144831
- fix alternative removal on postun
- update trigger

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Thu Dec 20 2007 Adam Williamson <awilliamson@mandriva.org> 2.13.2-22mdv2008.1
+ Revision: 135392
- drop bogus requires on tclx allowing it to be removed from the distro
- don't package COPYING
- new license policy

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Fri Sep 07 2007 Anssi Hannula <anssi@mandriva.org> 2.13.2-21mdv2008.0
+ Revision: 82049
- rebuild for new soname of tcl

  + Thierry Vignaud <tv@mandriva.org>
    - kill desktop-file-validate's 'warning: key "Encoding" in group "Desktop Entry" is deprecated'

* Mon Aug 20 2007 Oden Eriksson <oeriksson@mandriva.com> 2.13.2-20mdv2008.0
+ Revision: 67908
- rebuilt against new portaudio libs

* Fri Jul 20 2007 Adam Williamson <awilliamson@mandriva.org> 2.13.2-19mdv2008.0
+ Revision: 53987
- rebuild against new lesstif
- update icon cache in %%post
- no need to mkdir if you're using install -D
- drop X-Mandriva menu category
- buildrequires autoconf

* Fri Jun 01 2007 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 2.13.2-18mdv2008.0
+ Revision: 34274
- Removed old menu, placed icons in directories following
  freedesktop.org standard.


* Wed Dec 13 2006 Per Øyvind Karlsen <pkarlsen@mandriva.com> 2.13.2-17mdv2007.0
+ Revision: 96138
- Fix flac mess
- U?\195pdate buildrequires for libflac
- add new flac patch

* Fri Oct 13 2006 Nicolas Lécureuil <neoclust@mandriva.org> 2.13.2-16mdv2007.1
+ Revision: 63854
- increase release
- Fix patches
-  Fix Build for portaudio V19
- Import TiMidity++

* Tue Sep 12 2006 Per Øyvind Karlsen <pkarlsen@mandriva.com> 2.13.2-15mdv2007.0
- force linking against nas with -laudio to fix build on x86_64

* Tue Aug 29 2006 Per Øyvind Karlsen <pkarlsen@mandriva.com> 2.13.2-14mdv2007.0
- build against x.org's xaw, not Xaw3d
- xdg menu
- cosmetics

* Thu Jun 08 2006 Per Øyvind Karlsen <pkarlsen@mandriva.com> 2.13.2-13mdv2007.0
- fix build of nas against new modular x

* Wed Feb 15 2006 Christiaan Welvaart <cjw@daneel.dyndns.org> 2.13.2-12mdk
- buildRequires: tcl tk => libtcl-devel libtk-devel

* Sun Jan 01 2006 Oden Eriksson <oeriksson@mandriva.com> 2.13.2-11mdk
- rebuilt against soname aware deps

* Fri Sep 02 2005 Nicolas Lécureuil <neoclust@mandriva.org> 2.13.2-10mdk
- Removing Requires as it is still done ( but i have not found 
		yet how to really fix this! any ideas ?)
	- close ticket #18121

* Wed Aug 31 2005 Nicolas Lécureuil <neoclust@mandriva.org> 2.13.2-9mdk
- Fix Requires

* Fri Aug 05 2005 Nicolas Lécureuil <neoclust@mandriva.org> 2.13.2-8mdk
- Fix Build for gcc4

* Sun May 01 2005 Christiaan Welvaart <cjw@daneel.dyndns.org> 2.13.2-7mdk
- add BuildRequires: tcl liboggflac-devel

* Sat Apr 30 2005 Stew Benedict <sbenedict@mandriva.com> 2.13.2-6mdk
- rebuild for new libFLAC

* Thu Mar 10 2005 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 2.13.2-5mdk
- stick to timidity data in /usr/lib/timidity

* Tue Feb 22 2005 Abel Cheung <deaddog@mandrake.org> 2.13.2-4mdk
- assorted CVS fixes

* Sun Feb 20 2005 Abel Cheung <deaddog@mandrake.org> 2.13.2-3mdk
- Rebuild to fix changelog

* Sun Feb 20 2005 Abel Cheung <deaddog@mandrake.org> 2.13.2-2mdk
- *NOTE: Please only modify /etc/timidity/timidity-custom.cfg in the future
  and use update-alternatives to set it to manual mode, if you want to
  use your own patches and soundfonts
- Tidy up this poor forgotten child
- P0: Use /etc/timidity/timidity.cfg as default config location
- P1: Fix speex header detection
- P2: Fix default program path for emacs inteface and install emacs file
      when dynamic module is enabled
- P3: Fix wishx path in tcl scripts
- S2: Add emacs mode file
- Make GUI interface modular
- Split some interfaces into subpackage to reduce dependency
- Include freepats config as a template into TiMidity, so that people can
  use it as basis, and modify it to suite their own taste

* Fri Dec 03 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 2.13.2-1mdk
- 2.13.2
- from UTUMI Hirosi <utuhiro78@yahoo.co.jp>:
	o new release
	o add --enable-xaw, --enable-audio=vorbis
	o (try $ timidity -iat)
	o modify BuildRequires for --enable-xaw and --enable-audio=vorbis
	o modify timidity.cfg (Source1) to reduce cpu usage
	o (disable chorus, resample, reverb)

* Fri Jul 23 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 2.13.1-0.cvs20040722.1mdk
- update to cvs to have gtk+ interface working

* Sun May 23 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 2.13.0-2mdk
- fix buildrequires

* Thu Apr 22 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 2.13.0-1mdk
- 2.13.0
- drop all patches (fixed upstream)
- fix buildrequires (lib64..)
- fix non-conffile-in-etc

