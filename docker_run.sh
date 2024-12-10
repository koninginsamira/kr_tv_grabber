#!/bin/bash

sudo docker run -d \
  --name="$@" \
  -e PUID=1000 \
  -e PGID=1000 \
  -e GUIDE_FILENAME=guide-kr `# optional` \
  -e BACKUP_COUNT=7 `# optional` \
  -e RESTART_TIME=00:00 `# optional` \
  -e TZ=Etc/UTC \
  -v /etc/localtime:/etc/localtime:ro \
  -v ./docker/data:/data \
  -v ./docker/config/kr_tv_grabber:/config \
  --restart unless-stopped \
  "$@"