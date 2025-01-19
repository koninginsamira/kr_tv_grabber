#!/bin/bash

bash /app/cron.sh "python /app/app.py" > /proc/1/fd/1 2>/proc/1/fd/2 &
bash /app/host.sh "data" > /proc/1/fd/1 2>/proc/1/fd/2 &