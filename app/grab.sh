#!/bin/bash

echo "Grabbing guide..."

CONFIG_PATH="config"
GUIDE_PATH="data"

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
HOST="1.1.1.1"
PING_CMD="ping -c 1 $HOST"
DNS_CMD="getent hosts $HOST"

if $DNS_CMD > /dev/null && $PING_CMD &> /dev/null; then
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