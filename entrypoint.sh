#!/bin/bash

# Reset options
USER=""
GROUP=""
APP_PATHS=()
ROOT_MODE=""
BEFORE=""
APP=""

# Parse options. Each character represents an option:
# - 'u' for the username
# - 'g' for the group name
# - 'f' for the app folder
# - 'r' for toggling running the app as root
# - 'b' for running commands before the app
# - 'a' for the app command
while getopts "u:g:f:r:b:a:" opt; do
  case $opt in
    u) USER="$OPTARG" ;;
    g) GROUP="$OPTARG" ;;
    f) APP_PATHS+=("$OPTARG") ;;
    r) ROOT_MODE="$OPTARG" ;;
    b) BEFORE="$OPTARG" ;;
    a) APP="$OPTARG" ;;
    *)
      echo "Error: '$opt' was not recognised as a valid option"
      exit 1
      ;;
  esac
done

# Ensure the group exists
if ! getent group "$PGID" >/dev/null; then
    groupadd -g "$PGID" "$GROUP"

    if [ $? -eq 0 ]; then
        echo "Added new group '"$GROUP"' with ID '"$PGID"'"
    else
        exit 1
    fi
fi

# Ensure the user exists
if ! id -u "$PUID" >/dev/null 2>&1; then
    useradd -u "$PUID" -g "$PGID" -m "$USER"

    if [ $? -eq 0 ]; then
        echo "Added new user '"$USER"' with ID '"$PUID"'"
    else
        exit 1
    fi
fi

# Set permissions
for APP_PATH in "${APP_PATHS[@]}"; do
    echo "Changing ownership of '"$APP_PATH"' to '"$PUID:$PGID"'..."
    chown -R "$PUID:$PGID" "$APP_PATH"
    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to change ownership of '"$APP_PATH"'"
        exit 1
    fi
done

if [ -n "$BEFORE" ]; then
    $BEFORE
fi

if [[ "${ROOT_MODE^^}" == "TRUE" ]]; then
    exec $APP
else
    exec gosu "$PUID:$PGID" $APP
fi