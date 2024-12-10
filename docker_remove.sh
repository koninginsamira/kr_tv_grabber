#!/bin/bash

sudo docker stop "$@"
sudo docker remove "$@"