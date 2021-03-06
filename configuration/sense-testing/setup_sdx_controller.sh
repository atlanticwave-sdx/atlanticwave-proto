#!/bin/bash

# Package installation
sudo yum install -y docker git


# Docker user modifications?
sudo groupadd docker
sudo usermod -aG docker $USER
rm -rf ~/.docker
sudo systemctl enable docker

# Pull down the latest and greatest
git clone https://github.com/atlanticwave-sdx/atlanticwave-proto.git
cd ~/atlanticwave-proto/
#cp configuration/helloworld-multi/helloworld.manifest docker/sdx_container/
#cp configuration/helloworld-multi/helloworld.manifest docker/lc_container/

# Docker work - Build SDX Controller and Local Controller containers
sudo service docker restart

cd docker/sdx_container
sudo docker build -t sdx_container .
#rm helloworld.manifest

cd ../lc_container
sudo docker build -t lc_container .
#rm helloworld.manifest

# Network configuration
sudo /sbin/sysctl -w net.ipv4.conf.all.forwarding=1
docker network create sox-sdx-net
