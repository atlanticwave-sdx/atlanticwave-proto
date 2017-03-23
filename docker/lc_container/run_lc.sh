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

cd atlanticwave-proto/
git pull

cd localctlr/
python LocalController.py -n $SITE -m $MANIFEST -H $SDXIP

