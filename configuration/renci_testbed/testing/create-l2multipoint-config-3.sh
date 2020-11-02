#!/bin/bash

PWD=`pwd`
FILE="${PWD}/config_file_l2multipoint_3.txt"


echo "" > ${FILE}

EP1="rencis2"
EP2="dukes1"
EP3="uncs1"
EP1_PORT="4"
EP2_PORT="12"
EP3_PORT="12"
((EP1_VLAN=1001))
((EP2_VLAN=2001))
((EP3_VLAN=3001))
((BW=10000000))


for i in `seq 1 25`; do
   echo "$i  ${EP1} ${EP2} ${EP3} ${EP1_PORT} ${EP2_PORT} ${EP3_PORT} ${EP1_VLAN} ${EP2_VLAN} ${EP3_VLAN} ${BW}" >> ${FILE}
   (( EP1_VLAN = EP1_VLAN + 1 ))
   (( EP2_VLAN = EP2_VLAN + 1 ))
   (( EP3_VLAN = EP3_VLAN + 1 ))
   #(( BW = BW + 1000000 ))
done
  

EP1="rencis2"
EP2="ncsus1"
EP3="uncs1"
EP1_PORT="4"
EP2_PORT="12"
EP3_PORT="12"
((EP1_VLAN=1101))
((EP2_VLAN=2101))
((EP3_VLAN=3101))
((BW=10000000))

for i in `seq 26 50`; do
   echo "$i  ${EP1} ${EP2} ${EP3} ${EP1_PORT} ${EP2_PORT} ${EP3_PORT} ${EP1_VLAN} ${EP2_VLAN} ${EP3_VLAN} ${BW}" >> ${FILE}
   (( EP1_VLAN = EP1_VLAN + 1 ))
   (( EP2_VLAN = EP2_VLAN + 1 ))
   (( EP3_VLAN = EP3_VLAN + 1 ))
   #(( BW = BW + 1000000 ))
done

EP1="ncsus1"
EP2="dukes1"
EP3="uncs1"
EP1_PORT="12"
EP2_PORT="12"
EP3_PORT="12"
((EP1_VLAN=1201))
((EP2_VLAN=2201))
((EP3_VLAN=3201))
((BW=10000000))

for i in `seq 51 75`; do
   echo "$i  ${EP1} ${EP2} ${EP3} ${EP1_PORT} ${EP2_PORT} ${EP3_PORT} ${EP1_VLAN} ${EP2_VLAN} ${EP3_VLAN} ${BW}" >> ${FILE}
   (( EP1_VLAN = EP1_VLAN + 1 ))
   (( EP2_VLAN = EP2_VLAN + 1 ))
   (( EP3_VLAN = EP3_VLAN + 1 ))
   #(( BW = BW + 1000000 ))
done

EP1="ncsus1"
EP2="dukes1"
EP3="uncs1"
EP1_PORT="12"
EP2_PORT="12"
EP3_PORT="12"
((EP1_VLAN=1301))
((EP2_VLAN=2301))
((EP3_VLAN=3301))
((BW=10000000))

for i in `seq 76 100`; do
   echo "$i  ${EP1} ${EP2} ${EP3} ${EP1_PORT} ${EP2_PORT} ${EP3_PORT} ${EP1_VLAN} ${EP2_VLAN} ${EP3_VLAN} ${BW}" >> ${FILE}
   (( EP1_VLAN = EP1_VLAN + 1 ))
   (( EP2_VLAN = EP2_VLAN + 1 ))
   (( EP3_VLAN = EP3_VLAN + 1 ))
   #(( BW = BW + 1000000 ))
done


