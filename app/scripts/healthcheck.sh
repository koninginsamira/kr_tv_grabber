#!/bin/bash

# Check if grab is finished
last_line=$(tail -n 1 /config/last_run.txt)
if [[ "$last_line" != "finished" ]]; then
    echo "Grab has not finished"
    exit 1
else
    echo "Grab has finished"
fi

# Check if the file is hosted
if [[ "${HTTP^^}" == "TRUE" ]]; then
    HOST="localhost:${HTTP_PORT}"
    FILE_URL="${HOST}/${GUIDE_FILENAME}.xml"

    if ! curl --silent --fail "$FILE_URL" > /dev/null; then
        echo "File '${FILENAME}' is not accessible on '${HOST}'"
        exit 1
    else
        echo "File '${FILENAME}' is accessible on '${HOST}'"
    fi
else
    echo "Hosting is turned off, skipping this check.."
fi

# Check if the cron job is running
if ! pgrep supercronic > /dev/null; then
    echo "Cron job is not running"
    exit 1
else
    echo "Cron job is running"
fi

echo "Healthcheck passed"
exit 0