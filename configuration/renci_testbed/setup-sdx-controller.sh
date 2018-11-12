#!/bin/bash

# yum work
sudo yum -y update
sudo yum -y install git docker.io

#sudo groupadd docker #Already added
sudo usermod -aG docker $USER

# git work
git clone https://github.com/RENCI-NRIG/atlanticwave-sdx/atlanticwave-proto.git
git checkout renci_testbed_setup

# Docker work: build SDX Controller container
cd ~/atlanticwave-proto/
cp configuration/renci_testbed/renci_ben.manifest docker/sdx_container/

sudo systemctl restart docker

cd docker/sdx_container
sudo docker build -t sdx_container .
rm renci_ben.manifest 

# Copy over run scripts
cd ~/atlanticwave-proto/configuration/renci_testbed
cp start-sdx-controller.sh ~
