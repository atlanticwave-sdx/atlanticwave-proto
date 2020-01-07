#/bin/bash

#OPTS="dit"
OPTS="it"
NAME="sdxrencitestbed"

# SDX Controller
cd atlanticwave-proto/sdxctlr/

SDX_CONTAINER=$(docker ps -a -f name=${NAME} -q)

if [[ -n "${SDX_CONTAINER}" ]]; then
    docker stop ${SDX_CONTAINER}
fi

docker run --rm --network host -e MANIFEST="/renci_ben_1.manifest" -e IPADDR="0.0.0.0" -e PORT="5000" -e LCPORT="5555" -p 5000:5000 -p 5555:5555 -${OPTS} --name=${NAME} sdx_container
