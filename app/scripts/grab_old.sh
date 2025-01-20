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
# if [ -f "$TMP_FILE" ]; then
#     rm "$TMP_FILE"
#     echo "Leftover files were removed"
# fi

# Check internet connection
HOST="1.1.1.1"
PING_CMD="ping -c 1 $HOST"
DNS_CMD="getent hosts $HOST"

echo "Connecting to the internet..."
if $DNS_CMD > /dev/null && $PING_CMD &> /dev/null; then
    # Grab guide
    # npx tv_grab_kr --days "$FUTURE_THRESHOLD" --output "$TMP_FILE"

    # Check for error
    if [ $? -eq 0 ]; then
        echo "Guide was grabbed"

        # Add a <date> tag to each <programme>
        xmlstarlet ed -L -s '//programme' -t elem -n date -v "" "$TMP_FILE"

        # Fill new <date> tag with date from @start
        xmlstarlet ed -L -u '//programme/date' -x "substring(//programme/@start, 1, 8)" "$TMP_FILE"

        echo "Copied programme start date to separate date tag"

        # Add old programmes to new guide
        if [ -n ${NEW_BACKUP+x} ]; then
            CURRENT_DATE=$(date --utc +%Y%m%d%H%M%S)
            HISTORY_THRESHOLD_DATE=$(date --utc -d "$HISTORY_THRESHOLD days ago" +%Y%m%d%H%M%S)

            # Extract the <programme> tags from the back-up file
            xmlstarlet sel -t -m '//programme' -v '@start' -n "$NEW_BACKUP" | \

            while read START_TIME; do
                # Extract the date and time part (first 14 characters) and timezone part (last 5 characters)
                TIMESTAMP=$(echo "$START_TIME" | sed 's/\(..............\) \(....\)/\1/')
                TIMEZONE=$(echo "$START_TIME" | sed 's/.\{14\}//')

                # Convert the timestamp (YYYYMMDDHHMMSS) into a comparable format using date
                TIMESTAMP_COMPARABLE=$(date -d "${TIMESTAMP:0:4}-${TIMESTAMP:4:2}-${TIMESTAMP:6:2} ${TIMESTAMP:8:2}:${TIMESTAMP:10:2}:${TIMESTAMP:12:2} ${TIMEZONE}" +%Y%m%d%H%M%S)

                # Compare the timestamp from the old guide with the given threshold
                if [[ "$TIMESTAMP_COMPARABLE" > "$HISTORY_THRESHOLD_DATE" ]]; then
                    # Extract the full <programme> element if the condition is met
                    xmlstarlet sel -t -m "//programme[@start='$START_TIME']" -c . "$NEW_BACKUP"
                fi
            done | \
            # Now merge valid <programme> elements into file1.xml
            xmlstarlet ed -s /root -t elem -n "dummy" -v "$(cat)" "$TMP_FILE" > "$(TMP_FILE)001"
        fi

        # Move generated guide to target location
        cp "$TMP_FILE" "$TARGET_FILE"

        # Remove leftover files
        rm "$TMP_FILE"
        
        echo "Guide file created at '$TARGET_FILE'"
    else
        echo "Error: Something went wrong while grabbing, no guide file was created"
    fi
else
    echo "Error: Could not connect to the internet. No guide file was created"
fi