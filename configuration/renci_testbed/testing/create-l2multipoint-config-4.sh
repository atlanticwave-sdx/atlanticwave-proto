#!/bin/bash

PWD=`pwd`
FILE="${PWD}/config_file_l2multipoint_4.txt"


echo "" > ${FILE}

EP1="rencis2"
EP2="dukes1"
EP3="uncs1"
EP4="ncsus1"
EP1_PORT="4"
EP2_PORT="12"
EP3_PORT="12"
EP4_PORT="12"
((EP1_VLAN=1001))
((EP2_VLAN=2001))
((EP3_VLAN=3001))
((EP4_VLAN=3501))
((BW=10000000))


for i in `seq 1 100`; do
   echo "$i  ${EP1} ${EP2} ${EP3} ${EP4} ${EP1_PORT} ${EP2_PORT} ${EP3_PORT} ${EP4_PORT} ${EP1_VLAN} ${EP2_VLAN} ${EP3_VLAN} ${EP4_VLAN} ${BW}" >> ${FILE}
   (( EP1_VLAN = EP1_VLAN + 1 ))
   (( EP2_VLAN = EP2_VLAN + 1 ))
   (( EP3_VLAN = EP3_VLAN + 1 ))
   (( EP4_VLAN = EP4_VLAN + 1 ))
   #(( BW = BW + 1000000 ))
done
  

