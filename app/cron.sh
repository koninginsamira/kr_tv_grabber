#!/bin/bash

# Ensure the RESTART_TIME variable is set
if [ -z "$RESTART_TIME" ]; then
    echo "RESTART_TIME is not set."
    exit 1
fi

# Parse the 24-hour time into hours and minutes
HOUR=$(echo "$RESTART_TIME" | cut -d':' -f1)
MINUTE=$(echo "$RESTART_TIME" | cut -d':' -f2)

# Validate the time format
if ! [[ "$HOUR" =~ ^[0-9]{1,2}$ && "$MINUTE" =~ ^[0-9]{1,2}$ ]]; then
    echo "Invalid TIME_24H format. Use HH:MM (e.g., 03:00). Exiting."
    exit 1
fi

# Ensure the hour and minute are within valid ranges
if [ "$HOUR" -lt 0 ] || [ "$HOUR" -gt 23 ] || [ "$MINUTE" -lt 0 ] || [ "$MINUTE" -gt 59 ]; then
    echo "Invalid TIME_24H value. Hour must be 0-23 and minute must be 0-59. Exiting."
    exit 1
fi

# Generate the cron syntax
CRON_TIME="$MINUTE $HOUR * * *"

# Write the cron job
echo -e "$CRON_TIME gosu "$PUID:$PGID" "$@"" > /app/cron

# Apply the cron job
echo "Adding '"$@"' as cron job at $RESTART_TIME..."
supercronic -passthrough-logs /app/cron