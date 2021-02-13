#!/bin/bash

if ! test $SITE
then 
  SITE="atl"
fi

if ! test $MANIFEST
then 
  MANIFEST="../demo/aw-three-site.manifest"
fi

if ! test $SPANNINGTREEMANIFEST
then 
  MANIFEST="../demo/aw-three-site_spanning_tree.manifest"
fi

if ! test $SDXIP
then 
  SDXIP="127.0.0.1"
fi

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

echo "--- Site for LC: $SITE"
echo "--- Manifest file: $MANIFEST"
echo "--- SDXIP: $SDXIP"
cd localctlr/
###python LocalController.py -n $SITE -m $MANIFEST -c $SPANNINGTREEMANIFEST -H $SDXIP
python LocalController.py -n $SITE -m $MANIFEST -H $SDXIP

