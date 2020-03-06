#/bin/bash

MODE="$2"
echo "--- MODE: $MODE"

if [ -z "$3" ]; then
  DOCKER_IMAGE_NAME="sdx_container"
else
  DOCKER_IMAGE_NAME=$3
fi

if [ "$MODE" == "detached" ]; then
  OPTS="dit"
else
  OPTS="it"
fi

NAME="sdxrencitestbed"

SDX_CONTAINER=$(docker ps -a -f name=${NAME} -q)

if [[ -n "${SDX_CONTAINER}" ]]; then
    docker stop ${SDX_CONTAINER}
fi

docker run --rm --network host -e MANIFEST="/renci_ben.manifest" -e IPADDR="0.0.0.0" -e PORT="5000" -e LCPORT="5555" -p 5000:5000 -p 5555:5555 -${OPTS} --name=${NAME} ${DOCKER_IMAGE_NAME}
