#/bin/bash

#OPTS="dit"
OPTS="it"

# SDX Controller
cd atlanticwave-proto/sdxctlr/
docker stop sdxrencitestbed
docker rm sdxrencitestbed
docker run -e MANIFEST="/renci_ben.manifest" -e IPADDR="0.0.0.0" -e PORT="5000" -e LCPORT="5555" -p 5000:5000 -p 5555:5555 -${OPTS} --name=sdxrencitestbed sdx_container

