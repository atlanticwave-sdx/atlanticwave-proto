#/bin/bash
set -x
SITE="$1"
export SITE
echo "--- $0 - SITE: $SITE"

MODE="$2"
echo "--- $0 - MODE: $MODE"

CONFIG="$3"
echo "--- $0 - CONFIG: $CONFIG"

MANIFEST="$4"
echo "--- $0 - MANIFEST: $MANIFEST"

if [ "$MODE" == "detached" ]; then
  OPTS="dit"
else
  OPTS="it"
fi


case ${SITE} in
    renci)
              RYU_PORT=6681
              LC_SITE="rencictlr"
              SDXIPVAL="10.14.11.254"
              #SDXIPVAL="10.13.11.10"
              export SDXIPVAL
              ;;
    duke)
              RYU_PORT=6682
              LC_SITE="dukectlr"
              SDXIPVAL="10.14.11.254"
              #SDXIPVAL="10.13.12.10"
              export SDXIPVAL
              ;;
    unc)
              RYU_PORT=6683
              LC_SITE="uncctlr"
              SDXIPVAL="10.14.11.254"
              #SDXIPVAL="10.13.13.10"
              export SDXIPVAL
              ;;
    ncsu)
              RYU_PORT=6684
              LC_SITE="ncsuctlr"
              SDXIPVAL="10.14.11.254"
              #SDXIPVAL="10.13.14.10"
              export SDXIPVAL
              ;;
    \?)
              echo "Invalid option" >&2
              exit 1
              ;;
esac

echo "--- $0 - LC_SITE: $LC_SITE"
echo "--- $0 - RYU_PORT: $RYU_PORT"

# Local Controller
cd atlanticwave-proto/localctlr/

LC_CONTAINER=$(docker ps -a -f name=${LC_SITE} -q)

if [[ -n "${LC_CONTAINER}" ]]; then
    docker stop ${LC_CONTAINER}
fi

#for i in `docker volume ls  -q` ; do docker volume rm $i; done
docker volume rm atlanticwave-proto
docker volume create atlanticwave-proto

docker run --rm --network host -v atlanticwave-proto:/atlanticwave-proto -e MANIFEST="/${MANIFEST}" -e SPANNINGTREEMANIFEST="/spanning_tree_${MANIFEST}" -e SITE="${LC_SITE}" -e SDXIP=${SDXIPVAL} -p ${RYU_PORT}:${RYU_PORT} -${OPTS} --name=${LC_SITE} lc_container

docker ps -a
