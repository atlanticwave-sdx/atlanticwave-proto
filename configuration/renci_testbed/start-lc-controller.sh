#/bin/bash

#OPTS="dit"
OPTS="it"

LC_SITE="lc-$1"
export LC_SITE

SDXIPVAL="10.14.10.254"
export SDXIPVAL

case ${LC_SITE} in
    lc-renci) 
              RYU_PORT=6681
              ;;
    lc-duke) 
              RYU_PORT=6682
              ;;
    lc-unc) 
              RYU_PORT=6683
              ;;
    lc-ncsu) 
              RYU_PORT=6684
              ;;
    \?)
              echo "Invalid option" >&2
              exit 1
              ;;
esac


# Local Controller
cd atlanticwave-proto/localctlr/
docker stop ${LC_SITE}
docker rm ${LC_SITE}

docker run --rm --network host -e MANIFEST="/renci_ben.manifest" -e SITE="${LC_SITE}" -e SDXIP=${SDXIPVAL} -p ${RYU_PORT}:${RYU_PORT} -${OPTS} --name=${LC_SITE} lc_container

echo "The IP of the VM is:"
ifconfig | awk '/inet addr/{print substr($2,6)}' | awk '/192.168/{print}'
