#/bin/bash

#
cd ../../sdxctlr/
docker rm sdxhelloworld
docker run -e MANIFEST="/helloworld.manifest" -e IPADDR="172.17.0.2" -e PORT="5000" -e LCPORT="5555" -p 5000:5000 -it --name=sdxhelloworld sdx_container
