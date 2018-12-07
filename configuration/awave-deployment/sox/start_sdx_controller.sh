#!/bin/bash

# Variables used for nearly everything
source variables.sh

# stop existing SDX container
docker stop $SDX_CONTAINTER_NAME

# Start new SDX container
docker run -e MANIFEST=$MANIFEST_FILE -e IPADDR=$SDX_IPADDR -e PORT=$SDX_PORT -e LCPORT=$SDX_LCPORT -e PYTHONPATH=$PYTHON_PATH -e AWAVEDIR=$CONTAINER_AWAVE_DIRECTORY -p $SDX_PORT:$SDX_PORT -v $SDX_VOLUMES -it -name=$SDX_CONTAINER_NAME sdx_container $SDX_START_COMMAND
#FIXME: outbound ports for APIs?
