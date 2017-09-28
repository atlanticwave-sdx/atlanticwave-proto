#/bin/bash

#
cd ../../localctlr/
docker rm lchelloworld
docker run -e MANIFEST="/helloworld.manifest" -e SITE="br1" -e SDXIP="127.0.0.1" -p 6680:6680 -it --name=lchelloworld lc_container


