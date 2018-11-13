#/bin/bash

LC_SITE="lc-$1"
export LC_SITE

# Local Controller
cd atlanticwave-proto/localctlr/
docker stop ${LC_SITE}
docker rm ${LC_SITE}
export SDXIPVAL="10.14.11.254"
docker run -e MANIFEST="/renci_ben.manifest" -e SITE="${LC_SITE}" -e SDXIP=${SDXIPVAL} -p 6680:6680 -dit --name=${LC_SITE} lc_container


echo "The IP of the VM is:"
ifconfig | awk '/inet addr/{print substr($2,6)}' | awk '/192.168/{print}'
