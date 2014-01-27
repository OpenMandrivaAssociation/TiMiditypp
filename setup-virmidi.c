/*
 * Automatically set up a virtual MIDI device with TiMidity++
 * (C) 2014 OpenMandriva Association
 * Released under the GPLv3+
 * Written by Bernhard Rosenkränzer <bero@lindev.ch>
 */

#include <sys/types.h>
#include <stdio.h>
#include <unistd.h>
#include <grp.h>
#include <limits.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>

static uint32_t get_aconnect_device(char *dev) {
	FILE *aconnect = popen("LANG=C LC_ALL=C /usr/bin/aconnect -o", "r");
	if(!aconnect)
		return 0xffffffff;
	char buf[512];
	int client = -1, device = -1;
	char *d=(char*)malloc(strlen(dev)+2);
	*d='\'';
	strcpy(d+1, dev);
	while(!feof(aconnect)) {
		fgets(buf, 512, aconnect);
		if(!strncmp(buf, "client ", 7)) {
			client = atoi(buf+7);
		} else if(client >= 0 && strstr(buf, d)) {
			char *c = buf;
			while(isspace(*c))
				c++;
			device = atoi(c);
			break;
		}
	}
	pclose(aconnect);
	if (client < 0 || device < 0)
		return 0xffffffff;
	return (client << 16) + device;
}

int main(int argc, char **argv) {
	struct group *audio_grp = getgrnam("audio");
	if(!audio_grp) {
		fprintf(stderr, "No audio group found\n");
		return 1;
	}
	gid_t gids[NGROUPS_MAX];
	int g = getgroups(NGROUPS_MAX, gids);
	if(g < 0) {
		perror("getgroups");
		return 1;
	}
	bool in_audio_group = false;
	for(int i = 0; i < g; i++) {
		if(gids[i] == audio_grp->gr_gid) {
			in_audio_group = true;
			break;
		}
	}
	if(!in_audio_group) {
		fprintf(stderr, "You need to be in group audio\n");
		return 2;
	}
	uint32_t timidityDev = get_aconnect_device("TiMidity");
	if(timidityDev == 0xffffffff) {
		system("/usr/bin/systemctl --user start timidity");
		sleep(2);
		timidityDev = get_aconnect_device("TiMidity");
	}
	if(timidityDev == 0xffffffff) {
		fprintf(stderr, "Can't detect or create TiMidity++ device\n");
		return 3;
	}

	uid_t user = getuid();
	setuid(0);
	system("/sbin/modprobe snd-virmidi");
	setreuid(user, user);

	uint32_t virmidiDev = get_aconnect_device("VirMIDI");
	char buf[512];
	snprintf(buf, 512, "aconnect %u:%u %u:%u", virmidiDev >> 16, virmidiDev & 0xffff, timidityDev >> 16, timidityDev & 0xffff);
	puts(buf);
	system(buf);
	return 0;
}
