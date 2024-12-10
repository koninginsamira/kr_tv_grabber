#!/bin/bash

APP_APP_PATHS=()

# Parse options. Each character represents an option:
# - 'u' for the username
# - 'g' for the group name
# - 'f' for the app folder
# - 'a' for the app command
while getopts "u:g:f:a:" opt; do
  case $opt in
    u) USER="$OPTARG" ;;
    g) GROUP="$OPTARG" ;;
    f) APP_APP_PATHS+=("$OPTARG") ;;
    a) APP="$OPTARG" ;;
    *)
      echo "Error: '$opt' was not recognised as a valid option"
      exit 1
      ;;
  esac
done

# Ensure the group exists
if ! getent group "$PGID" >/dev/null; then
    groupadd -g "$PGID" $GROUP
    echo "Added new group '$GROUP' with ID '$PGID'"
fi

# Ensure the user exists
if ! id -u "$PUID" >/dev/null 2>&1; then
    useradd -u "$PUID" -g "$PGID" -m $USER
    echo "Added new user '$USER' with ID '$PUID'"
fi

# Set permissions
for APP_PATH in "${APP_APP_PATHS[@]}"; do
    echo "Changing ownership of '$APP_PATH' to '$PUID:$PGID'..."
    chown -R "$PUID:$PGID" "$APP_PATH"
    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to change ownership of '$APP_PATH'"
        exit 1
    fi
done

exec gosu "$PUID:$PGID" $APP