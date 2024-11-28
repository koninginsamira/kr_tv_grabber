#!/bin/bash

GUIDE_PATH="data/"
FILE="$GUIDE_PATH$GUIDE_FILE.xml"

# Check if the required variables are set
if [ -z "$GUIDE_FILE" ] || [ -z "$BACKUP_COUNT" ] || [ -z "$RESTART_TIME" ]; then
    echo "Error: GUIDE_FILE, BACKUP_COUNT or RESTART_TIME is not set."
    exit 1
fi

# Check if the file exists
if [ -f "$FILE" ]; then
    # Base name of the file
    BASE_NAME=$(basename "$FILE")
    DIR_NAME=$(dirname "$FILE")

    echo "Guide file '$FILE' already exists"

    # Find the next available bak number
    for i in $(seq -w 1 $BACKUP_COUNT); do
        NEW_FILE="$DIR_NAME/$BASE_NAME.bak$i"
        if [ ! -e "$NEW_FILE" ]; then
            # Add the bak extension
            cp "$FILE" "$NEW_FILE"
            echo "Backup created at '$NEW_FILE'"
            
            # Remove next bak file if it exists
            NEXT_FILE="$DIR_NAME/$BASE_NAME.bak$((($i % $BACKUP_COUNT) + 1))"
            if [ -f "$NEXT_FILE" ]; then
                rm "$NEXT_FILE"
                echo "The maximum backup count ($BACKUP_COUNT) has been reached, removed '$NEXT_FILE'"
            fi

            break
        fi
    done
else
    echo "Guide file '$FILE' does not yet exist"
fi

# Grab guide
tv_grab_kr --days 3 --output $FILE
echo "Guide file created at '$FILE'"

# Wait for specific time
CURRENT_EPOCH=$(date +%s)
TARGET_EPOCH=$(date -d "$RESTART_TIME today" +%s)
if (( CURRENT_EPOCH >= TARGET_EPOCH )); then
    TARGET_EPOCH=$(date -d "$RESTART_TIME tomorrow" +%s)
fi

SLEEP_SECONDS=$(( $TARGET_EPOCH - $CURRENT_EPOCH ))

echo "Waiting for $SLEEP_SECONDS seconds until the next $RESTART_TIME..."
sleep $SLEEP_SECONDS

# Restart
exec ./run.sh