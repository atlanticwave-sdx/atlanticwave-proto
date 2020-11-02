#!/bin/bash

#set -x
#SRC_SW="rencis1"
#DST_SW="dukes1"
#SRC_PORT=12
#DST_PORT=12
#SRC_VLAN=1421
#DST_VLAN=1422

SRC_SW=$1
DST_SW=$2
SRC_VLAN=$3
DST_VLAN=$4
SRC_PORT=12
DST_PORT=12
BANDWIDTH=800000
START=`date "+%Y-%m-%dT%H:%M:%S"`
END=`date --date="3 days" "+%Y-%m-%dT%H:%M:%S"`

SDX_CONTROLLER="atlanticwave-sdx-controller.renci.ben"
SDX_CONT_PORT=5000
REST_ENDPOINT="http://${SDX_CONTROLLER}:${SDX_CONT_PORT}/api/v1/policies/type/L2Tunnel"
COOKIE="cookie-mcevik.txt"

curl \
-X POST ${REST_ENDPOINT} \
-b ${COOKIE} \
-H "Content-Type: application/json" \
--data-binary @- << EOF 
{
  "L2Tunnel":
    {
      "starttime":"${START}",
      "endtime":"${END}",
      "srcswitch":"${SRC_SW}","dstswitch":"${DST_SW}",
      "srcport":${SRC_PORT},"dstport":${DST_PORT},
      "srcvlan":${SRC_VLAN},"dstvlan":${DST_VLAN},
      "bandwidth":${BANDWIDTH}
    }
}
EOF

