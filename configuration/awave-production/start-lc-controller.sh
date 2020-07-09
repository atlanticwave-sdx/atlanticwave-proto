#/bin/bash

SITE="$1"
export SITE
echo "--- SITE: $SITE"

MODE="$2"
echo "--- MODE: $MODE"

CONFIG="$3"
echo "--- CONFIG: $CONFIG"

MANIFEST="$4"
echo "--- MANIFEST: $MANIFEST"

if [ "$MODE" == "detached" ]; then
  OPTS="dit"
else
  OPTS="it"
fi


SDXIPVAL="10.14.11.254"
export SDXIPVAL

case ${SITE} in
    atl)
              RYU_PORT=6681
              LC_SITE="atlctlr"
              ;;
    mia)
              RYU_PORT=6682
              LC_SITE="miactlr"
              ;;
    chl)
              RYU_PORT=6683
              LC_SITE="chlctlr"
              ;;
    \?)
              echo "Invalid option" >&2
              exit 1
              ;;
esac


# Local Controller
cd atlanticwave-proto/localctlr/

LC_CONTAINER=$(docker ps -a -f name=${LC_SITE} -q)

if [[ -n "${LC_CONTAINER}" ]]; then
    docker stop ${LC_CONTAINER}
fi

#for i in `docker volume ls  -q` ; do docker volume rm $i; done
docker volume rm atlanticwave-proto
docker volume create atlanticwave-proto

docker run --rm --network host -v atlanticwave-proto:/atlanticwave-proto -e MANIFEST="/${MANIFEST}" -e SITE="${LC_SITE}" -e SDXIP=${SDXIPVAL} -p ${RYU_PORT}:${RYU_PORT} -${OPTS} --name=${LC_SITE} lc_container

docker ps -a
