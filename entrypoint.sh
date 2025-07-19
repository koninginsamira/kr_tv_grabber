#!/bin/bash

# Reset options
USER=""
GROUP=""
APP_PATHS=()
ROOT_MODE=""
TITLE=""
BEFORE=""
APP=""
AFTER=""

# Parse options. Each character represents an option:
# - 'u' for the username
# - 'g' for the group name
# - 'f' for the app folder
# - 'r' for toggling running the app as root
# - 't' for showing the title
# - 'b' for running commands before the main script
# - 'm' for the main script
# - 'a' for running a script after the main script
while getopts "u:g:f:r:t:b:m:a:" opt; do
  case $opt in
    u) USER="$OPTARG" ;;
    g) GROUP="$OPTARG" ;;
    f) APP_PATHS+=("$OPTARG") ;;
    r) ROOT_MODE="$OPTARG" ;;
    t) TITLE="$OPTARG" ;;
    b) BEFORE="$OPTARG" ;;
    m) APP="$OPTARG" ;;
    a) AFTER="$OPTARG" ;;
    *)
      echo "Error: \"$opt\" was not recognised as a valid option."
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
        echo "Added new group \""$GROUP"\" with ID \""$PGID"\"."
    else
        echo "Could not add group \""$GROUP"\" with ID \""$PGID"\"."
        exit 1
    fi
fi
echo "Group \""$GROUP"\" with ID \""$PGID"\" will be used."

# Ensure the user exists
if ! id -u "$PUID" >/dev/null 2>&1; then
    useradd -u "$PUID" -g "$PGID" -m "$USER"

    if [ $? -eq 0 ]; then
        echo "Added new user \""$USER"\" with ID \""$PUID"\"."
    else
        echo "Could not add user \""$USER"\" with ID \""$PUID"\"."
        exit 1
    fi
fi
echo "User \""$USER"\" with ID \""$PUID"\" will be used."

# Set permissions
if (( ${#APP_PATHS[@]} != 0 )); then
    echo ""
    for APP_PATH in "${APP_PATHS[@]}"; do
        echo "Changing ownership of \""$APP_PATH"\" to \""$PUID:$PGID"\"..."
        chown -R "$PUID:$PGID" "$APP_PATH"
        if [[ $? -ne 0 ]]; then
            echo "Error: Failed to change ownership of \""$APP_PATH"\"."
            exit 1
        fi
    done
fi

if [ -n "$BEFORE" ]; then
    echo ""
    echo "Running script before starting the app..."
    $BEFORE
fi

after() {
    echo ""
    echo "Container was stopped."

    if [ -n "$AFTER" ]; then
        echo ""
        echo "Running script after stopping the app..."
        $AFTER
    fi
}

trap 'after' SIGTERM

echo ""
echo "Starting the app..."
echo ""

if [[ "${ROOT_MODE^^}" == "TRUE" ]]; then
    $APP &
else
    gosu "$PUID:$PGID" env PATH="$PATH" $APP &
fi

wait $!