#!/bin/bash

# Variables used for nearly everything
source variables.sh

# Stop existing SENSE orchestrator 
docker stop $SENSE_CONTAINER_NAME
docker rm $SENSE_CONTAINER_NAME

# Start new SENSE orchestrator
docker run -p $SENSE_PORT_ONE:$SENSE_PORT_ONE -p $SENSE_PORT_TWO:$SENSE_PORT_TWO -e KC_SERVER=$SENSE_KC_SERVER --name $SENSE_CONTAINER_NAME -i -t docker.io/mail2xiyang/stackv
