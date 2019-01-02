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
  LCPORT=5555
fi
echo "LC Port: $LCPORT"

if ! test $AWAVEDIR
then
  cd atlanticwave-proto/
  git pull
else
  cd $AWAVEDIR
fi

cd sdxctlr/
python SDXController.py -m $MANIFEST -H $IPADDR -p $PORT -l $LCPORT -N

