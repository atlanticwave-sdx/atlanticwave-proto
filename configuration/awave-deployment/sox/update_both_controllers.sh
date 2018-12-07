#!/bin/bash

# Environment Variables?

# Stop both controllers
./stop_both_controllers.sh

# Update the git repo
git pull

# Restart both controllers
./start_both_controllers.sh
