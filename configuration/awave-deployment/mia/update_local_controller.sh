#!/bin/bash

# Environment Variables?

# Stop controller
./stop_local_controller.sh

# Update the git repo
git pull

# Restart controller
./start_both_controllers.sh
