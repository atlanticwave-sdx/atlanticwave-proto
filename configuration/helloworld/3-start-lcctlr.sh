#/bin/bash

#
cd ../../localctlr/
docker rm lchelloworld
docker run -e MANIFEST="../configuration/helloworld/helloworld.manifest" -e SITE="atl" -e SDXIP="127.0.0.1" -p 6633:6633 -it --name=lchelloworld lc_container


