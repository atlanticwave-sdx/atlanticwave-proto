#!/bin/bash

TEMP_FILE=/tmp/trap.txt
CONFIG_DIR="/var/tmp"
TMP_DIR="/var/tmp"
WORK_DIR="/root"


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
esac

#SITE=$(hostnamectl --transient | cut -d- -f3 | cut -d. -f1) # renci | duke | unc | ncsu
#TYPE=$(hostnamectl --transient | cut -d- -f2 ) # sdx | lc 

AW_REPO="https://github.com/RENCI-NRIG/atlanticwave-proto.git"
AW_BRANCH="master-rci"


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
    docker rmi ${TYPE}_container
}


build_docker_image(){
   REPO=$1
   BR=$2
   TMP_DIR=$3
   WORK_DIR=$4
   TYPE=$5
   
   cd $TMP_DIR
   title "Clone Branch ${AW_BRANCH}"
   git clone -b $BR $REPO
   cp ${TMP_DIR}/atlanticwave-proto/configuration/renci_testbed/setup-${TYPE}-controller.sh ${WORK_DIR}
   chmod +x ${WORK_DIR}/setup-${TYPE}-controller.sh 
   cd ${WORK_DIR}
   ./setup-${TYPE}-controller.sh -R ${AW_REPO} -B ${AW_BRANCH}

}


run_docker_container(){
   SITE=$1
   WORK_DIR=$2
   TYPE=$3
   MODE=$4

   # Run Docker Container ( renci | duke | unc | ncsu )
   cd ${WORK_DIR}
   ./start-${TYPE}-controller.sh ${SITE} ${MODE}
}


stop_docker_container(){
   for i in `docker ps -a -q`; do echo "--- Container: $i" ; docker stop $i; docker rm -v $i; done
}


while getopts "R:B:m:cbrsH" opt; do
    case $opt in
        R)
            AW_REPO=${OPTARG}
            ;;
        B)
            AW_BRANCH=${OPTARG}
            ;;
        m)
            MODE=${OPTARG}
            ;;
        c)
            title "Cleanup Files"
            cleanup_files ${TMP_DIR} ${WORK_DIR} ${TYPE}
            
            title "Cleanup Docker Containers and Images"
            cleanup_docker ${TYPE}
            ;;
        b)
            title "Cleanup Files"
            cleanup_files ${TMP_DIR} ${WORK_DIR} ${TYPE}
            title "Cleanup Docker Containers and Images"
            cleanup_docker ${TYPE}
            title "Build Docker Image"
            build_docker_image $AW_REPO $AW_BRANCH $TMP_DIR $WORK_DIR ${TYPE}
            ;;
        r)
            title "Run Docker Container for ${TYPE} - MODE: $MODE"
            run_docker_container $SITE $WORK_DIR $TYPE $MODE
            ;;
        s)
            title "Stop Docker Containers"
            stop_docker_container 
            ;;
        H)
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


