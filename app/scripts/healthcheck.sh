#!/bin/bash

# Check if the file is hosted
if [[ "${HTTP^^}" == "TRUE" ]]; then
    HOST="localhost:${HTTP_PORT}"
    FILE_URL="${HOST}/${GUIDE_FILENAME}.xml"

    if ! curl --silent --fail "$FILE_URL" > /dev/null; then
    echo "File '${FILENAME}' is not accessible on '${HOST}'"
    exit 1
    fi
fi

# Check if the cron job is running
if ! pgrep supercronic > /dev/null; then
    echo "Cron job is not running"
    exit 1
fi

echo "Healthcheck passed"
exit 0