#!/bin/bash

# The xxx_START_COMMAND variables can be empty.

LOCAL_AWAVE_DIRECTORY="~/atlanticwave-proto"
CONTAINER_AWAVE_DIRECTORY="/development"
MANIFEST_FILE="/development/configuration/awave-deployment/awave.manifest"
PYTHON_PATH=".:/development/"

LC_CONTAINER_NAME="sox_local_controller"
LC_VOLUMES="$LOCAL_AWAVE_DIRECTORY:$CONTAINER_AWAVE_DIRECTORY:rw"
LC_IP_ADDR=""
LC_PORT=""
LC_SITE="sox"
LC_SDXIP=""
LC_START_COMMAND=""


SDX_CONTAINER_NAME="sox_sdx_controller"
SDX_VOLUMES="$LOCAL_AWAVE_DIRECTORY:$CONTAINER_AWAVE_DIRECTORY:rw"
SDX_IPADDR=""
SDX_PORT=""
SDX_LCPORT=""
SDX_START_COMMAND=""

