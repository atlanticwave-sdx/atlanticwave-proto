#/bin/bash

echo "Type 'help' for details on how to use Mininet"
echo "There are four nodes: atl, atldtn, mia, miadtn"
# Start Mininet!
cd atlanticwave-proto/configuration-multi/helloworld-multi/
sudo python helloworld-mn-topo.py
