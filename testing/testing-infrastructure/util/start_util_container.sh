#!/bin/bash

CONTAINER_NAME="util_container"
CTLR_PORT=6633

docker stop $CONTAINER_NAME

docker run -p $CTLR_PORT:$CTLR_PORT -it --name=$CONTAINER_NAME util_container
