#!/bin/bash

if [[ "${HTTP^^}" == "TRUE" ]]; then
    # Ensure the HTTP_PORT variable is set
    if [ -z "$HTTP_PORT" ]; then
        echo "[http] HTTP_PORT is not set."
        echo ""
        exit 1
    fi

    # Start HTTP server
    echo "[http] Starting HTTP server on port $HTTP_PORT..."
    python3 -m http.server $HTTP_PORT --directory "$@"

    # Check for error
    if [ $? -ne 0 ]; then
        echo "[http] Error: HTTP server could not be started"
        echo ""
        exit 1
    fi
fi