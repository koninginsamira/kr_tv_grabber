#!/bin/bash

CONFIG_PATH="config"
GUIDE_PATH="data"

# Create folders if they do not exist
mkdir -p $CONFIG_PATH;
mkdir -p $GUIDE_PATH;

# Check if the required variables are set
if [ -z "$GUIDE_FILENAME" ] || [ -z "$BACKUP_COUNT" ] || [ -z "$RESTART_TIME" ]; then
    echo "Error: GUIDE_FILENAME, BACKUP_COUNT or RESTART_TIME is not set."
    exit 1
fi

TARGET_FILE="$GUIDE_PATH/$GUIDE_FILENAME.xml"
TMP_FILE="$CONFIG_PATH/$GUIDE_FILENAME.tmp"

# Check if the file exists
if [ -f "$TARGET_FILE" ]; then
    echo "Guide file '$TARGET_FILE' already exists"

    # Find the next available bak number
    for i in $(seq -w 1 $BACKUP_COUNT); do
        NEW_BACKUP="$CONFIG_PATH/$GUIDE_FILENAME.bak$i"
        if [ ! -e "$NEW_BACKUP" ]; then
            # Add the bak extension
            cp "$TARGET_FILE" "$NEW_BACKUP"
            echo "Backup created at '$NEW_BACKUP'"
            
            # Remove next bak file if it exists
            NEXT_BACKUP="$CONFIG_PATH/$GUIDE_FILENAME.bak$((($i % $BACKUP_COUNT) + 1))"
            if [ -f "$NEXT_BACKUP" ]; then
                rm "$NEXT_BACKUP"
                echo "The maximum backup count ($BACKUP_COUNT) has been reached, removed '$NEXT_BACKUP'"
            fi

            break
        fi
    done
else
    echo "Guide file '$TARGET_FILE' does not yet exist"
fi

# Remove leftover files
if [ -f "$TMP_FILE" ]; then
    rm "$TMP_FILE"
fi

# Check internet connection
echo -e "GET http://google.com HTTP/1.0\n\n" | nc google.com 80 > /dev/null 2>&1

if [ $? -eq 0 ]; then
    # Grab guide
    npx tv_grab_kr --days 3 --output "$TMP_FILE"

    # Check for error
    if [ $? -eq 0 ]; then
        # Move new guide to target location
        cp "$TMP_FILE" "$TARGET_FILE"
        rm "$TMP_FILE"
        echo "Guide file created at '$TARGET_FILE'"
    else
        echo "Error: Something went wrong while grabbing, no guide file was created"
    fi
else
    echo "Error: Could not connect to the internet. No guide file was created"
fi

# Calculate time left until next RESTART_TIME
CURRENT_EPOCH=$(date +%s)
TARGET_EPOCH=$(date -d "$RESTART_TIME today" +%s)
if (( CURRENT_EPOCH >= TARGET_EPOCH )); then
    TARGET_EPOCH=$(date -d "$RESTART_TIME tomorrow" +%s)
fi

SLEEP_SECONDS=$(( $TARGET_EPOCH - $CURRENT_EPOCH ))

# Wait for specific time
echo "Waiting for $SLEEP_SECONDS seconds until the next $RESTART_TIME..."
sleep $SLEEP_SECONDS

# Restart
exec ./run.sh