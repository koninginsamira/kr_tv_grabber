#!/bin/bash

if [[ "${HTTP^^}" == "TRUE" ]]; then
    # Ensure the HTTP_PORT variable is set
    if [ -z "$HTTP_PORT" ]; then
        echo "HTTP_PORT is not set."
        exit 1
    fi

    # Start HTTP server
    echo "Starting HTTP server on port $HTTP_PORT..."
    python3 -m http.server $HTTP_PORT --directory "$@"

    # Check for error
    if [ $? -ne 0 ]; then
        echo "Error: HTTP server could not be started"
    fi
fi