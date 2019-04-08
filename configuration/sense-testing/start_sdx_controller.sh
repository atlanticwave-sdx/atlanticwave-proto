#!/bin/bash

# Variables used for nearly everything
source variables.sh

# stop existing SDX container
docker stop $SDX_CONTAINER_NAME
docker rm $SDX_CONTAINER_NAME

# Start new SDX container
docker run -e MANIFEST=$MANIFEST_FILE -e IPADDR=$SDX_IPADDR -e PORT=$SDX_EXTERNAL_PORT -e LCPORT=$SDX_LCPORT -e PYTHONPATH=$PYTHON_PATH -e AWAVEDIR=$CONTAINER_AWAVE_DIRECTORY -p $SDX_EXTERNAL_PORT:$SDX_EXTERNAL_PORT -p $SDX_LC_PORT:$SDX_LC_PORT -p $SDX_SENSE_PORT:$SDX_SENSE_PORT -v $SDX_VOLUMES --network $SOX_DOCKER_NETWORK -it --name=$SDX_CONTAINER_NAME sdx_container $SDX_START_COMMAND
#FIXME: outbound ports for APIs?
