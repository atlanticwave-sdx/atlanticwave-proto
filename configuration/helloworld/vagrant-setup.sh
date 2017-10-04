#!/bin/bash

# apt work
sudo apt update
sudo apt install -y git mininet docker.io

#sudo groupadd docker #Already added
sudo usermod -aG docker $USER


# git work
git clone https://github.com/atlanticwave-sdx/atlanticwave-proto.git

# Docker work: build SDX Controller and Local Controller containers
cd ~/atlanticwave-proto/
cp configuration/helloworld/helloworld.manifest docker/sdx_container/
cp configuration/helloworld/helloworld.manifest docker/lc_container/

sudo service docker restart

cd docker/sdx_container
sudo docker build -t sdx_container .
rm helloworld.manifest

cd ../lc_container
sudo docker build -t lc_container .
rm helloworld.manifest

# Copy over run scripts
cd ~/atlanticwave-proto/configuration/helloworld
cp 1-start-sdxctlr.sh ~
cp 2-start-lcctlr.sh ~
cp 3-start-mininet.sh ~
cp 4-get-ip.sh
