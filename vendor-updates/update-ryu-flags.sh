#!/bin/bash

if [ -z $1 ]; then
  echo "Usage: update-ryu-dns.sh [location of Ryu]"
  exit
fi

cp -n $1/ryu/flags.py $1/ryu/flags.orig
echo "CONF.register_cli_opts([" >> $1/ryu/flags.py
echo "    cfg.StrOpt('lcip', default='127.0.0.1', help='Local Controller IP'),"  >> $1/ryu/flags.py
echo "    cfg.IntOpt('ryu-cxn-port', default=55767, help='Port for RYU controller communication')"  >> $1/ryu/flags.py
echo "], group='atlanticwave')" >> $1/ryu/flags.py

# Saved a backup of __init__.py, just in case.
#sed -i.bak 's/)/, dns)/' $1/ryu/lib/packet/__init__.py
