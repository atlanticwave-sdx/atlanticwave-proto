#!/bin/bash

# apt work
sudo apt update

sudo apt install -y git docker.io
#sudo groupadd docker #Already added
sudo usermod -aG docker $USER

sudo apt install -y pypy3 python3-pip python3-venv

sudo update-alternatives --remove python /usr/bin/python2
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 10

git clone git://github.com/mininet/mininet
mininet/util/install.sh -nfv

# git work
git clone -b python3upgrade https://github.com/atlanticwave-sdx/atlanticwave-proto.git

# Docker work: build SDX Controller and Local Controller containers
cd ~/atlanticwave-proto/
cp configuration/helloworld-multi-vagrant/helloworld.manifest docker/sdx_container/
cp configuration/helloworld-multi-vagrant/helloworld.manifest docker/lc_container/

sudo service docker restart

cd docker/sdx_container
sudo docker build -t sdx_container .
rm helloworld.manifest

cd ../lc_container
sudo docker build -t lc_container .
rm helloworld.manifest

# Copy over run scripts
cd ~/atlanticwave-proto/configuration/helloworld-multi-vagrant
cp 1-start-controller.sh ~
cp 2-start-topology.sh ~
