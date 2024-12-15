#!/bin/bash

if [[ "${HTTP^^}" == "TRUE" ]]; then
    # Ensure the HTTP_PORT variable is set
    if [ -z "$HTTP_PORT" ]; then
        echo "HTTP_PORT is not set."
        exit 1
    fi

    # Start HTTP server
    echo "Starting HTTP server on port $HTTP_PORT..."
    busybox httpd -p $HTTP_PORT -h /data

    # Check for error
    if [ $? -eq 0 ]; then
        echo "HTTP server is online on port $HTTP_PORT"
    else
        echo "Error: HTTP server could not be started"
    fi
fi