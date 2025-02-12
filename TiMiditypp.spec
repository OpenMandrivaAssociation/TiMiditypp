# Stick to /usr/lib/timidity on any platform
# XXX probably better in /usr/share/timidity for arch independent data
# but it's not worth splitting that much

%define timiditydir	/usr/lib/timidity

#
# When big change is involved (e.g. timidity.cfg change location),
# so that new timidity binray and old patch RPM won't work together,
# increment this number by 1 for all timidity related RPMs
#
%define patch_pkg_version 2

%define git %{nil}

#
# NOTE: When updating config for midia patch set, please refresh both
# config file included here and the one in patch pkg
#

%define _disable_lto 1

Summary:	MIDI to WAVE converter and player
Name:		TiMidity++
Version:	2.15.0
%if "%git" == ""
Release:	6
Source0:	http://freefr.dl.sourceforge.net/project/timidity/TiMidity%2B%2B/TiMidity%2B%2B-%version/TiMidity%2B%2B-%version.tar.xz
%else
Release:	0.%{git}.1
# git clone git://git.code.sf.net/p/timidity/git timidity
Source0:	timidity-%{git}.tar.xz
%endif
URL:		https://timidity.sourceforge.net/
License:	GPLv2+
Group:		Sound
Source1:	http://www.timidity.jp/dist/cfg/timidity.cfg
Source2:	timidity-emacs-mode.el
Source3:	timidity.README.mdv
Source5:	setup-virmidi.c
Source11:	%{name}48.png
Source12:	%{name}32.png
Source13:	%{name}16.png
# (Abel) change default config path to /etc/timidity/timidity.cfg
Patch0:		timidity-2.13.2-default-config-path.patch
Patch1:		timidity-clang-buildfixes.patch
Patch2:		TiMidity-2.15.0-compile.patch
Patch8:		timidity-2.13.2-tcl-legacy.patch
Requires:	timidity-instruments = %{patch_pkg_version}
BuildRequires:	pkgconfig(alsa)
BuildRequires:	autoconf
BuildRequires:	emacs-bin
BuildRequires:	pkgconfig(gtk+-x11-2.0)
BuildRequires:	pkgconfig(jack)
BuildRequires:	motif-devel
BuildRequires:	pkgconfig(ao)
BuildRequires:	pkgconfig(flac) >= 1.1.3
BuildRequires:	nas-devel
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	pkgconfig(ogg)
BuildRequires:	pkgconfig(vorbis)
BuildRequires:	pkgconfig(portaudio-2.0)
BuildRequires:	pkgconfig(speex)
BuildRequires:	pkgconfig(tcl)
BuildRequires:	pkgconfig(tk)
BuildRequires:	pkgconfig(xaw7)
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
%if "%git" != ""
%setup -q -n timidity
%else
%setup -q
%endif
%autopatch -p1

%build
touch ChangeLog
libtoolize --force
aclocal -I autoconf
autoheader
automake --add-missing --foreign
autoconf

# little ugly trick to force install of tclIndex, running wish requires
# X display
touch interface/tclIndex

%configure \
	--with-ao-libraries=%{_libdir} \
	--with-libFLAC-libraries=%{_libdir} \
	--with-ogg-libraries=%{_libdir} \
	--with-libOggFLAC-libraries=%{_libdir} \
	--with-vorbis-libraries=%{_libdir} \
	--enable-audio=oss,alsa,nas,portaudio,jack,ao,vorbis,flac,speex \
	--enable-dynamic=dynamic,ncurses,slang,motif,tcltk,emacs,xaw,xskin,gtk \
	--enable-interface=alsaseq \
	--enable-network \
	--enable-server \
	--with-libraries=%{_libdir}



%make LDFLAGS="-laudio -lFLAC"

%__cc %optflags -std=gnu99 -o setup-virmidi %{SOURCE5}

%install
rm -rf %{buildroot}
%makeinstall_std
install -d %{buildroot}%{_datadir}/timidity
install -m644 %{SOURCE1} -D %{buildroot}%{_sysconfdir}/timidity/timidity-custom.cfg

install -m 4755 setup-virmidi %{buildroot}%{_bindir}/

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

# create systemd service
mkdir -p %buildroot%_prefix/lib/systemd/user/default.target.wants
cat >%buildroot%_prefix/lib/systemd/user/timidity.service <<"EOF"
[Unit]
Description=TiMidity++ MIDI playback system
After=pulseaudio.socket

[Service]
ExecStart=%_bindir/timidity -iA -OO

[Install]
WantedBy=default.target
EOF

cat >%buildroot%_prefix/lib/systemd/user/virmidi.service <<"EOF"
[Unit]
Description=Virtual MIDI device
After=timidity.service

[Service]
Type=oneshot
ExecStart=%_bindir/setup-virmidi

[Install]
WantedBy=default.target
EOF
ln -s ../timidity.service %buildroot%_prefix/lib/systemd/user/default.target.wants/timidity.service
ln -s ../virmidi.service %buildroot%_prefix/lib/systemd/user/default.target.wants/virmidi.service

%post
%{_sbindir}/update-alternatives --install %{_sysconfdir}/timidity/timidity.cfg timidity.cfg %{_sysconfdir}/timidity/timidity-custom.cfg 10

%postun
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
%attr(4755,root,root) %{_bindir}/setup-virmidi
%{_mandir}/man?/timidity*
%lang(ja) %{_mandir}/ja/man?/*
%{_datadir}/timidity
%dir %{timiditydir}
%timiditydir/if_ncurses.so
%{_datadir}/applications/mandriva-%{name}.desktop
%{_iconsdir}/hicolor/16x16/apps/%{name}.png
%{_iconsdir}/hicolor/32x32/apps/%{name}.png
%{_iconsdir}/hicolor/48x48/apps/%{name}.png
%_prefix/lib/systemd/user/*.service
%_prefix/lib/systemd/user/default.target.wants/*.service

%files interfaces-extra
%defattr(-,root,root)
%doc doc/C/README.{tk,xaw,xskin}
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/*.el
%{_datadir}/emacs/site-lisp/*.el
%timiditydir/if_emacs.so
%timiditydir/if_gtk.so
%timiditydir/if_motif.so
%timiditydir/if_slang.so
%timiditydir/if_tcltk.so
%timiditydir/if_xaw.so
%timiditydir/if_xskin.so
%{timiditydir}/*.tcl
%{timiditydir}/tclIndex
