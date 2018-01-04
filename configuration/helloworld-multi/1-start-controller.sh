#/bin/bash

# SDX Controller
cd atlanticwave-proto/sdxctlr/
docker rm sdxhelloworld
docker run -e MANIFEST="/helloworld.manifest" -e IPADDR="0.0.0.0" -e PORT="5000" -e LCPORT="5555" -p 5000:5000 -dit --name=sdxhelloworld sdx_container
sleep 3



# Local Controller
cd ../localctlr/
docker rm westctlr
docker rm centctlr
docker rm eastctlr
SDXIPVAL="172.17.0.2"
docker run -e MANIFEST="/helloworld.manifest" -e SITE="br1" -e SDXIP=$SDXIPVAL -p 6680:6680 -dit --name=westctlr lc_container
docker run -e MANIFEST="/helloworld.manifest" -e SITE="br1" -e SDXIP=$SDXIPVAL -p 6681:6681 -dit --name=centctlr lc_container
docker run -e MANIFEST="/helloworld.manifest" -e SITE="br1" -e SDXIP=$SDXIPVAL -p 6682:6682 -dit --name=eastctlr lc_container



# Display IP 
echo "The IP of the VM is:"
ifconfig | awk '/inet addr/{print substr($2,6)}' | awk '/192.168/{print}'
