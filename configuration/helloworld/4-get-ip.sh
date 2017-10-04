#/bin/bash

echo "The IP of the VM is:"
ifconfig | awk '/inet addr/{print substr($2,6)}' | awk '/192.168/{print}'
