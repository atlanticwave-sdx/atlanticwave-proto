#!/bin/bash

if ! test $SITE
then 
  SITE="atl"
fi
echo "Site for LC: $SITE"


if ! test $MANIFEST
then 
  MANIFEST="../demo/aw-three-site.manifest"
fi
echo "Manifest file: $MANIFEST"

if ! test $SDXIP
then 
  SDXIP="127.0.0.1"
fi
  echo "SDXIP: $SDXIP"

if ! test $AWAVEDIR
then
  cd atlanticwave-proto/
  git pull
else
  rm `pip3 show ryu | grep Location: | awk '{print $NF}'`/ryu/flags.py
  cp `pip3 show ryu | grep Location: | awk '{print $NF}'`/ryu/flags.orig `pip show ryu | grep Location: | awk '{print $NF}'`/ryu/flags.py
  cd $AWAVEDIR
  ./vendor-updates/update-ryu-flags.sh `pip show ryu | grep Location: | awk '{print $NF}'`
fi

cd localctlr/
python LocalController.py -n $SITE -m $MANIFEST -H $SDXIP

