#/bin/bash

MODE="$2"
echo "--- MODE: $MODE"

if [ "$MODE" == "detached" ]; then
  OPTS="dit"
else
  OPTS="it"
fi

NAME="sdxrencitestbed"

# SDX Controller
cd atlanticwave-proto/sdxctlr/

SDX_CONTAINER=$(docker ps -a -f name=${NAME} -q)

if [[ -n "${SDX_CONTAINER}" ]]; then
    docker stop ${SDX_CONTAINER}
fi

#for i in `docker volume ls  -q` ; do docker volume rm $i; done
docker volume rm atlanticwave-proto
docker volume create atlanticwave-proto

docker run --rm --network host -v atlanticwave-proto:/atlanticwave-proto -e MANIFEST="/renci_ben.manifest" -e IPADDR="0.0.0.0" -e PORT="5000" -e LCPORT="5555" -p 5000:5000 -p 5555:5555 -${OPTS} --name=${NAME} sdx_container
