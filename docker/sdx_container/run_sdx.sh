#!/bin/bash

if ! test $MANIFEST
then 
  MANIFEST="../demo/aw-three-site.manifest"
fi
echo "Manifest file: $MANIFEST"

if ! test $IPADDR
then 
  IPADDR="0.0.0.0"
fi
echo "IP Address: $IPADDR"

if ! test $PORT
then 
  PORT=5000
fi
echo "Port: $PORT"

if ! test $LCPORT
then 
  PORT=5555
fi
echo "LC Port: $LCPORT"

cd atlanticwave-proto/
git pull

cd sdxctlr/
python SDXController.py -m $MANIFEST -H $IPADDR -p $PORT -l $LCPORT

