#!/bin/bash

TEMP_FILE=/tmp/trap.txt
CONFIG_DIR="/var/tmp"
TMP_DIR="/var/tmp"
WORK_DIR="$HOME"


DELAY=3 
DATE=$(date +%Y%m%d-%H%M%S)
PWD=`pwd`

HOSTNAME=$(hostname)

case ${HOSTNAME} in
    bf40g1.renci.ben)
            SITE="renci"
            TYPE="lc"
            ;;
    bf40g1.duke.ben)
            SITE="duke"
            TYPE="lc"
            ;;
    bf40g1.unc.ben)
            SITE="unc"
            TYPE="lc"
            ;;
    bf40g1.ncsu.ben)
            SITE="ncsu"
            TYPE="lc"
            ;;
    atlanticwave-sdx-controller.renci.ben)
            SITE="renci"
            TYPE="sdx"
            ;;
    s1)
            SITE="mia"
            TYPE="lc"
            ;;
    awsdx-ctrl.cloud.rnoc.gatech.edu)
            SITE="atl"
            TYPE="lc"
            ;;
    dtn01.ls.lsst.org)
            SITE="chl"
            TYPE="lc"
            ;;
    awsdx-app.cloud.rnoc.gatech.edu)
            SITE="atl"
            TYPE="sdx"
            ;;
#    sdxlc.ampath.net)
#            SITE="mia"
#            TYPE="lc"
#            ;;
#    awsdx-ctrl.cloud.rnoc.gatech.edu)
#            SITE="atl"
#            TYPE="lc"
#            ;;
#    acanets-chile)
#            SITE="chl"
#            TYPE="lc"
#            ;;
#    awsdx-app.cloud.rnoc.gatech.edu)
#            SITE="atl"
#            TYPE="sdx"
#            ;;
esac

#SITE=$(hostnamectl --transient | cut -d- -f3 | cut -d. -f1) # renci | duke | unc | ncsu
#TYPE=$(hostnamectl --transient | cut -d- -f2 ) # sdx | lc 

AW_REPO="https://github.com/atlanticwave-sdx/atlanticwave-proto.git"
#AW_BRANCH="mcevik-production-deployment"
AW_BRANCH="master"
AW_CONFIG="awave-production"
AW_MANIFEST="awave-production.manifest"
MODE="attached"

clean_up (){

        # Perform program exit housekeeping
        echo "--- ERROR" > $TEMP_FILE 2>&1
        exit
}

trap clean_up SIGHUP SIGINT SIGTERM


faillog() {
  echo "$1" >&2
}


fail() {
  faillog "ERROR: $@"
  clean_up
}


title(){
    echo ""
    echo "============================================================================== "
    echo "--- $1"
    echo "============================================================================== "
}


usage(){
    echo -e "   Usage: $0 [-c] [-b] [-r] [-H]"
    echo -e "\t -H: Usage"
    echo -e "\t -c: clean files"
    echo -e "\t -b: clean files and build docker image"
    echo -e "\t -r: run docker container"
    echo
}


cleanup_files(){
   TMP_DIR=$1
   WORK_DIR=$2
   TYPE=$3
   rm -rf ${TMP_DIR}/atlanticwave-proto
   rm -rf ${WORK_DIR}/atlanticwave-proto
   rm -rf ${WORK_DIR}/setup-${TYPE}-controller.sh 
   rm -rf ${WORK_DIR}/start-${TYPE}-controller.sh
}


cleanup_docker(){
    TYPE=$1
    for i in `docker ps -a -q`; do echo "--- Container: $i" ; docker stop $i; docker rm -v $i; done
    for i in `docker images | grep none | awk '{print $3}'`; do docker rmi $i ; done
}

delete_docker_images(){
    TYPE=$1
    for i in `docker ps -a -q`; do echo "--- Container: $i" ; docker stop $i; docker rm -v $i; done
    for i in `docker images -q`; do docker rmi $i ; done
}

build_docker_image(){
   REPO=$1
   BR=$2
   TMP_DIR=$3
   WORK_DIR=$4
   TYPE=$5
   CONFIG=$6
   MANIFEST=$7
   
   cd $TMP_DIR
   title "Clone Branch ${BR} - Configuration: ${CONFIG} - Manifest: ${MANIFEST}"
   git clone -b $BR $REPO
   cp ${TMP_DIR}/atlanticwave-proto/configuration/${CONFIG}/setup-${TYPE}-controller.sh ${WORK_DIR}
   chmod +x ${WORK_DIR}/setup-${TYPE}-controller.sh 
   cd ${WORK_DIR}
   ./setup-${TYPE}-controller.sh -R ${REPO} -B ${BR} -G ${CONFIG} -H ${MANIFEST}
}


build_docker_image_local(){
   REPO=$1
   BR=$2
   TMP_DIR=$3
   WORK_DIR=$4
   TYPE=$5
   CONFIG=$6
   MANIFEST=$7
   
   cd $TMP_DIR
   cp ${TMP_DIR}/atlanticwave-proto/configuration/${CONFIG}/setup-${TYPE}-controller.sh ${WORK_DIR}
   chmod +x ${WORK_DIR}/setup-${TYPE}-controller.sh 
   cd ${WORK_DIR}
   ./setup-${TYPE}-controller.sh -R ${REPO} -B ${BR} -G ${CONFIG} -H ${MANIFEST}

}

run_docker_container(){
   SITE=$1
   WORK_DIR=$2
   TYPE=$3
   MODE=$4
   CONFIG=$5
   MANIFEST=$6

   cd ${WORK_DIR}
   echo "--- $0 - SITE: $SITE "
   echo "--- $0 - MODE: $MODE "
   echo "--- $0 - CONFIG: $CONFIG"
   echo "--- $0 - MANIFEST: $MANIFEST"
   ./start-${TYPE}-controller.sh ${SITE} ${MODE} ${CONFIG} ${MANIFEST}
}


stop_docker_container(){
   for i in `docker ps -a -q`; do echo "--- Container: $i" ; docker stop $i; done
}


while getopts "R:B:G:H:m:S:T:cdbprsH" opt; do
    case $opt in
        R)
            AW_REPO=${OPTARG}
            ;;
        B)
            AW_BRANCH=${OPTARG}
            ;;
        G)
            # Set this to the directories under git atlanticwave-proto/configuration (eg. renci_testbed, awave-production)
            AW_CONFIG=${OPTARG}
            ;;
        H)
            AW_MANIFEST=${OPTARG}
            ;;
        m)
            MODE=${OPTARG}
            ;;
        S)
            SITE=${OPTARG}
            ;;
        T)
            TYPE=${OPTARG}
            ;;
        c)
            title "Cleanup Files"
            cleanup_files ${TMP_DIR} ${WORK_DIR} ${TYPE}
            
            title "Cleanup Docker Containers and Images"
            cleanup_docker ${TYPE}
            ;;
        d)
            title "Cleanup Files"
            cleanup_files ${TMP_DIR} ${WORK_DIR} ${TYPE}
            
            title "Cleanup Docker Containers and Images"
            delete_docker_images ${TYPE}
            ;;
        b)
            title "Cleanup Files"
            cleanup_files ${TMP_DIR} ${WORK_DIR} ${TYPE}
            title "Cleanup Docker Containers and Images"
            cleanup_docker ${TYPE}
            title "Build Docker Image"
            build_docker_image $AW_REPO $AW_BRANCH $TMP_DIR $WORK_DIR $TYPE $AW_CONFIG $AW_MANIFEST
            ;;
        p)
            title "Cleanup Docker Containers and Images"
            cleanup_docker ${TYPE}
            title "Build Docker Image"
            build_docker_image_local $AW_REPO $AW_BRANCH $TMP_DIR $WORK_DIR $TYPE $AW_CONFIG $AW_MANIFEST
            ;;
        r)
            title "Run Docker Container for TYPE: ${TYPE} - MODE: $MODE - SITE: $SITE - CONFIGURATION: $AW_CONFIG - MANIFEST: $AW_MANIFEST"
            echo "--- $0 - SITE: $SITE "
            echo "--- $0 - MODE: $MODE "
            echo "--- $0 - CONFIG: $CONFIG"
            echo "--- $0 - MANIFEST: $MANIFEST"
            run_docker_container $SITE $WORK_DIR $TYPE $MODE $AW_CONFIG $AW_MANIFEST
            #run_docker_container $SITE $AW_MANIFEST $AW_CONFIG 

            ;;
        s)
            title "Stop Docker Containers"
            stop_docker_container 
            ;;
        h)
            usage
            clean_up
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            clean_up
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            usage
            clean_up
            ;;
    esac
done


