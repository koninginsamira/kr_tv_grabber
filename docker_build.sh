#!/bin/bash

sudo docker build --no-cache -t "$@" . &> build.log