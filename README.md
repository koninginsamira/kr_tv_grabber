# XMLTV Grabber for Korean TV
Did you find a way to stream Korean television (perhaps through [this amazing resource](https://github.com/iptv-org/iptv?tab=readme-ov-file#grouped-by-language)), but you're still in need of a program guide to find out when Music Bank will air exactly?

__You're in luck!__

This script, and encompassing Docker container, will periodically grab the program guide for various Korean TV channels (using the wonderful [tv_grab_kr](https://github.com/axfree/tv_grab_kr)) and save it to a specified location in XMLTV format. This is especially useful in conjunction with streaming software such as [Plex](https://www.plex.tv/), [Emby](https://emby.media/) or [Jellyfin](https://jellyfin.org/). Either through [Threadfin](https://github.com/Threadfin/Threadfin) or directly.

## Requirements
* [Docker](https://www.docker.com/)

## Setup
To get started you'll have to create a container from this image. You can either use docker-compose or the docker cli for this.

### docker-compose (recommended)

```yaml
---
services:
  kr_tv_grabber:
    container_name: kr_tv_grabber
    image: ghcr.io/koninginsamira/kr_tv_grabber:main
    restart: unless-stopped
    environment:
      - PUID=1000
      - PGID=1000
      - GUIDE_FILENAME=guide-kr # optional
      - BACKUP_COUNT=7 # optional
      - RESTART_TIME=00:00 # optional
      - TZ=Etc/UTC
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./path/to/guide/location:/data
      - ./config/kr_tv_grabber:/config
```

### docker cli ([click here for more info](https://docs.docker.com/engine/reference/commandline/cli/))

```bash
docker run -d \
  --name=kr_tv_grabber \
  -e PUID=1000 \
  -e PGID=1000 \
  -e GUIDE_FILENAME=guide-kr `# optional` \
  -e BACKUP_COUNT=7 `# optional` \
  -e RESTART_TIME=00:00 `# optional` \
  -e TZ=Etc/UTC \
  -v /etc/localtime:/etc/localtime:ro \
  -v /path/to/guide/location:/data \
  -v /config/kr_tv_grabber:/config \
  --restart unless-stopped \
  ghcr.io/koninginsamira/kr_tv_grabber:main
```

## Parameters
| Parameter | Function |
| :----: | --- |
| `-e PUID=1000` | For UserID. |
| `-e PGID=1000` | For GroupID. |
| `-e GUIDE_FILENAME=guide-kr` | Change filename of output (NOTE: do __NOT__ include extension). |
| `-e BACKUP_COUNT=7` | Amount of backups to keep before overwriting old ones. |
| `-e RESTART_TIME=00:00` | Set the target time for which the script should wait before grabbing again. |
| `-e TZ=Etc/UTC` | Specify a timezone to use, see this [list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List). |
| `-v /data` | Location of target file, make sure your streaming software can access this path. |
| `-v /config` | Location of config folder, which stores temporary back-up files |

## Usage
Apart from the setup, everything else is automatic! It will immediately start the grabbing process once the container is run, after which it will wait until the next occurrence of the specified time. This will repeat indefinitely.
