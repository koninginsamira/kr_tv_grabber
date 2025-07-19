#!/bin/bash

last_line=$(tail -n 1 /config/last_run.txt)
if [[ "$last_line" == "started" ]]; then
    echo "Grab was still running, it will be stopped now."
    sed -i '$s/.*/stopped/' /config/last_run.txt
    exit 0
fi