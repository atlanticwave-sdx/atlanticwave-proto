#!/bin/bash

# Variables
source variables.sh

# Stop Local Controller
docker stop $LC_CONTAINER_NAME

# Stop SDX Controller
docker stop $SDX_CONTAINER_NAME
