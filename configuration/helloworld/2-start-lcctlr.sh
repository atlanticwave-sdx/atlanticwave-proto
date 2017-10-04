#/bin/bash

#
cd ../../localctlr/
docker rm lchelloworld
SDXIPVAL="172.17.0.2"
docker run -e MANIFEST="/helloworld.manifest" -e SITE="br1" -e SDXIP=$SDXIPVAL -p 6680:6680 -it --name=lchelloworld lc_container
