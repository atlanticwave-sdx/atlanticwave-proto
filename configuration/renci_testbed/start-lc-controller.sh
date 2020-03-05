#/bin/bash

SITE="$1"
export SITE

MODE="$2"
echo "--- MODE: $MODE"

if [-z "$3" ]; then
  DOCKER_IMAGE_NAME="lc_container"
else
  DOCKER_IMAGE_NAME=$3
fi

if [ "$MODE" == "detached" ]; then
  OPTS="dit"
else
  OPTS="it"
fi


SDXIPVAL="10.14.11.254"
export SDXIPVAL

case ${SITE} in
    renci)
              RYU_PORT=6681
              LC_SITE="rencictlr"
              ;;
    duke)
              RYU_PORT=6682
              LC_SITE="dukectlr"
              ;;
    unc)
              RYU_PORT=6683
              LC_SITE="uncctlr"
              ;;
    ncsu)
              RYU_PORT=6684
              LC_SITE="ncsuctlr"
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


docker run --rm --network host -e MANIFEST="/renci_ben.manifest" -e SITE="${LC_SITE}" -e SDXIP=${SDXIPVAL} -p ${RYU_PORT}:${RYU_PORT} -${OPTS} --name=${LC_SITE} ${DOCKER_IMAGE_NAME}

