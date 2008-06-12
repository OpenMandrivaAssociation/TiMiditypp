%define name	TiMidity++
%define version	2.13.2
%define release	%mkrel 23

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
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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
Requires:	timidity-instruments = %{patch_pkg_version}
BuildRequires:	alsa-lib-devel arts-devel autoconf emacs-bin esound-devel gtk2-devel
BuildRequires:	jackit-devel lesstif-devel libao-devel libflac-devel >= 1.1.3
BuildRequires:	liboggflac-devel nas-devel ncurses-devel oggvorbis-devel
BuildRequires:	portaudio-devel speex-devel libtcl-devel libtk-devel
BuildRequires:	libxaw-devel slang-devel
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
autoconf

# little ugly trick to force install of tclIndex, running wish requires
# X display
touch interface/tclIndex

%build
# (Abel) options are very confusing: interface names after --enable-dynamic are
# dynamically loaded, while those after --enable-interface are built-in
# alsa sequencer interface must be static, otherwise it can't be daemonized,
# nor can it use sched_setscheduler() to set real time priority

%configure2_5x \
	--enable-audio=oss,alsa,nas,arts,esd,portaudio,jack,ao,vorbis,flac,speex \
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

