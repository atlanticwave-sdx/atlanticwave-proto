#!/bin/bash

# apt work
sudo apt update
sudo apt install -y git mininet docker.io

#sudo groupadd docker #Already added
echo $USER
sudo usermod -aG docker $USER


# git work
git clone https://github.com/atlanticwave-sdx/atlanticwave-proto.git

# Docker work: build SDX Controller and Local Controller containers
cd ~/atlanticwave-proto/
pwd
pwd
pwd
cp configuration/helloworld/helloworld.manifest docker/sdx_container/
cp configuration/helloworld/helloworld.manifest docker/lc_container/

cd docker/sdx_container
docker build -t sdx_container .
rm helloworld.manifest

cd ../lc_container
docker build -t lc_container .
rm helloworld.manifest

