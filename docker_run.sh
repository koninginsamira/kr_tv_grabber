#!/bin/bash

sudo docker run -d \
  --name="$@" \
  -p 3501:3500 `# optional` \
  -e PUID=1000 \
  -e PGID=1000 \
  -e GUIDE_FILENAME=guide-kr `# optional` \
  -e BACKUP_COUNT=7 `# optional` \
  -e RESTART_TIME=04:20 `# optional` \
  -e HTTP=TRUE `# optional` \
  -e HTTP_PORT=3500 `# optional` \
  -e TZ=Europe/Amsterdam \
  -v /etc/localtime:/etc/localtime:ro \
  -v ./docker/data:/data \
  -v ./docker/config/kr_tv_grabber:/config \
  --restart unless-stopped \
  "$@"