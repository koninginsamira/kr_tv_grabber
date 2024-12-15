#!/bin/bash

source /app/host.sh > /proc/1/fd/1 2>/proc/1/fd/2 &
source /app/cron.sh > /proc/1/fd/1 2>/proc/1/fd/2 &
gosu "$PUID:$PGID" bash /app/grab.sh > /proc/1/fd/1 2>/proc/1/fd/2 &

wait