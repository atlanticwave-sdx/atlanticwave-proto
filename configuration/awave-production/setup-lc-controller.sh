#!/bin/bash

AW_REPO="https://github.com/atlanticwave-sdx/atlanticwave-proto.git"
AW_BRANCH="master"
AW_CONFIG="awave-production"
AW_MANIFEST="${AW_CONFIG}.manifest"

while getopts "R:B:G:H:" opt; do
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
    esac
done


# yum work
if [[ $EUID -eq 0 ]]; then
  sudo yum -y update
  sudo yum -y install git docker-ce
fi

#sudo groupadd docker #Already added
#sudo usermod -aG docker $USER

# git work
echo "--- $0 : AW_REPO  : ${AW_REPO}"
echo "--- $0 : AW_BRANCH: ${AW_BRANCH}"
echo "--- $0 : AW_CONFIG: ${AW_CONFIG}"
echo "--- $0 : AW_MANIFEST: ${AW_MANIFEST}"
git clone ${AW_REPO}

# Docker work: build Local Controller containers
cd atlanticwave-proto
git checkout ${AW_BRANCH}
cp configuration/${AW_CONFIG}/${AW_MANIFEST} docker/lc_container/

if [[ $EUID -eq 0 ]]; then
  sudo systemctl restart docker
  #sudo service docker restart
fi

cd docker/lc_container
sed -r -i "s/master/${AW_BRANCH}/g" Dockerfile
docker build -t lc_container .
rm -f ${AW_MANIFEST}

# Copy over run scripts
cd ../../configuration/${AW_CONFIG}
cp start-lc-controller.sh ~
