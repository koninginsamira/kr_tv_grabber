#!/bin/bash

# Reset options
USER=""
GROUP=""
APP_PATHS=()
ROOT_MODE=""
TITLE=""
BEFORE=""
APP=""

# Parse options. Each character represents an option:
# - 'u' for the username
# - 'g' for the group name
# - 'f' for the app folder
# - 'r' for toggling running the app as root
# - 't' for showing the title
# - 'b' for running commands before the app
# - 'a' for the app command
while getopts "u:g:f:r:t:b:a:" opt; do
  case $opt in
    u) USER="$OPTARG" ;;
    g) GROUP="$OPTARG" ;;
    f) APP_PATHS+=("$OPTARG") ;;
    r) ROOT_MODE="$OPTARG" ;;
    t) TITLE="$OPTARG" ;;
    b) BEFORE="$OPTARG" ;;
    a) APP="$OPTARG" ;;
    *)
      echo "Error: '$opt' was not recognised as a valid option"
      exit 1
      ;;
  esac
done

$TITLE

echo ""
echo "Running docker container..."
echo ""

# Ensure the group exists
if ! getent group "$PGID" >/dev/null; then
    groupadd -g "$PGID" "$GROUP"

    if [ $? -eq 0 ]; then
        echo "Added new group '"$GROUP"' with ID '"$PGID"'."
    else
        echo "Could not add group '"$GROUP"' with ID '"$PGID"'."
        exit 1
    fi
fi
echo "Group '"$GROUP"' with ID '"$PGID"' will be used."

# Ensure the user exists
if ! id -u "$PUID" >/dev/null 2>&1; then
    useradd -u "$PUID" -g "$PGID" -m "$USER"

    if [ $? -eq 0 ]; then
        echo "Added new user '"$USER"' with ID '"$PUID"'."
    else
        echo "Could not add user '"$USER"' with ID '"$PUID"'."
        exit 1
    fi
fi
echo "User '"$USER"' with ID '"$PUID"' will be used."

echo ""

# Set permissions
for APP_PATH in "${APP_PATHS[@]}"; do
    echo "Changing ownership of '"$APP_PATH"' to '"$PUID:$PGID"'..."
    chown -R "$PUID:$PGID" "$APP_PATH"
    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to change ownership of '"$APP_PATH"'"
        exit 1
    fi
done

echo ""

if [ -n "$BEFORE" ]; then
    echo "Running commands before starting the app..."
    $BEFORE
fi

echo ""
echo "Starting the app..."
echo ""

if [[ "${ROOT_MODE^^}" == "TRUE" ]]; then
    exec $APP
else
    exec gosu "$PUID:$PGID" env PATH="$PATH" $APP
fi