#/bin/bash

#
cd ../../localctlr/
docker rm lchelloworld
SDXIPVAL="$(ifconfig | awk '/inet addr/{print substr($2,6)}' | awk 'NR==1{print $1}')"
docker run -e MANIFEST="/helloworld.manifest" -e SITE="br1" -e SDXIP=$SDXIPVALl -p 6680:6680 -it --name=lchelloworld lc_container


