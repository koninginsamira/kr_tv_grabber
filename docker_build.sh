#!/bin/bash

sudo docker build --no-cache -t "$@" --build-arg USER=grabber --build-arg GROUP=grabber . &> build.log