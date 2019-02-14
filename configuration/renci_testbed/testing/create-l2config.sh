#!/bin/bash

PWD=`pwd`
FILE="${PWD}/config_file.txt"

SRC_SW="rencis1"
DST_SW="dukes1"
SRC_PORT="12"
DST_PORT="12"
((SRC_VLAN=1001))
((DST_VLAN=2001))
((BW=1000000))

for i in `seq 1 10`; do
   echo "$i  ${SRC_SW} ${DST_SW} ${SRC_PORT} ${DST_PORT} ${SRC_VLAN} ${DST_VLAN} ${BW}" >> ${FILE}
   (( SRC_VLAN = SRC_VLAN + 1 ))
   (( DST_VLAN = DST_VLAN + 1 ))
   (( BW = BW + 1000000 ))
done
  

SRC_SW="rencis1"
DST_SW="uncs1"
SRC_PORT="12"
DST_PORT="12"
((SRC_VLAN=1011))
((DST_VLAN=2011))
((BW=1000000))

for i in `seq 11 20`; do
   echo "$i  ${SRC_SW} ${DST_SW} ${SRC_PORT} ${DST_PORT} ${SRC_VLAN} ${DST_VLAN} ${BW}" >> ${FILE}
   (( SRC_VLAN = SRC_VLAN + 1 ))
   (( DST_VLAN = DST_VLAN + 1 ))
   (( BW = BW + 1000000 ))
done

SRC_SW="rencis1"
DST_SW="ncsus1"
SRC_PORT="12"
DST_PORT="12"
((SRC_VLAN=1021))
((DST_VLAN=2021))
((BW=1000000))

for i in `seq 21 30`; do
   echo "$i  ${SRC_SW} ${DST_SW} ${SRC_PORT} ${DST_PORT} ${SRC_VLAN} ${DST_VLAN} ${BW}" >> ${FILE}
   (( SRC_VLAN = SRC_VLAN + 1 ))
   (( DST_VLAN = DST_VLAN + 1 ))
   (( BW = BW + 1000000 ))
done

SRC_SW="dukes1"
DST_SW="rencis1"
SRC_PORT="12"
DST_PORT="12"
((SRC_VLAN=1031))
((DST_VLAN=2031))
((BW=1000000))

for i in `seq 31 40`; do
   echo "$i  ${SRC_SW} ${DST_SW} ${SRC_PORT} ${DST_PORT} ${SRC_VLAN} ${DST_VLAN} ${BW}" >> ${FILE}
   (( SRC_VLAN = SRC_VLAN + 1 ))
   (( DST_VLAN = DST_VLAN + 1 ))
   (( BW = BW + 1000000 ))
done

SRC_SW="dukes1"
DST_SW="uncs1"
SRC_PORT="12"
DST_PORT="12"
((SRC_VLAN=1041))
((DST_VLAN=2041))
((BW=1000000))

for i in `seq 41 50`; do
   echo "$i  ${SRC_SW} ${DST_SW} ${SRC_PORT} ${DST_PORT} ${SRC_VLAN} ${DST_VLAN} ${BW}" >> ${FILE}
   (( SRC_VLAN = SRC_VLAN + 1 ))
   (( DST_VLAN = DST_VLAN + 1 ))
   (( BW = BW + 1000000 ))
done

SRC_SW="dukes1"
DST_SW="ncsus1"
SRC_PORT="12"
DST_PORT="12"
((SRC_VLAN=1051))
((DST_VLAN=2051))
((BW=1000000))

for i in `seq 51 60`; do
   echo "$i  ${SRC_SW} ${DST_SW} ${SRC_PORT} ${DST_PORT} ${SRC_VLAN} ${DST_VLAN} ${BW}" >> ${FILE}
   (( SRC_VLAN = SRC_VLAN + 1 ))
   (( DST_VLAN = DST_VLAN + 1 ))
   (( BW = BW + 1000000 ))
done




SRC_SW="uncs1"
DST_SW="rencis1"
SRC_PORT="12"
DST_PORT="12"
((SRC_VLAN=1061))
((DST_VLAN=2061))
((BW=1000000))

for i in `seq 61 70`; do
   echo "$i  ${SRC_SW} ${DST_SW} ${SRC_PORT} ${DST_PORT} ${SRC_VLAN} ${DST_VLAN} ${BW}" >> ${FILE}
   (( SRC_VLAN = SRC_VLAN + 1 ))
   (( DST_VLAN = DST_VLAN + 1 ))
   (( BW = BW + 1000000 ))
done

SRC_SW="uncs1"
DST_SW="dukes1"
SRC_PORT="12"
DST_PORT="12"
((SRC_VLAN=1071))
((DST_VLAN=2071))
((BW=1000000))

for i in `seq 71 80`; do
   echo "$i  ${SRC_SW} ${DST_SW} ${SRC_PORT} ${DST_PORT} ${SRC_VLAN} ${DST_VLAN} ${BW}" >> ${FILE}
   (( SRC_VLAN = SRC_VLAN + 1 ))
   (( DST_VLAN = DST_VLAN + 1 ))
   (( BW = BW + 1000000 ))
done


SRC_SW="uncs1"
DST_SW="ncsus1"
SRC_PORT="12"
DST_PORT="12"
((SRC_VLAN=1081))
((DST_VLAN=2081))
((BW=1000000))

for i in `seq 81 90`; do
   echo "$i  ${SRC_SW} ${DST_SW} ${SRC_PORT} ${DST_PORT} ${SRC_VLAN} ${DST_VLAN} ${BW}" >> ${FILE}
   (( SRC_VLAN = SRC_VLAN + 1 ))
   (( DST_VLAN = DST_VLAN + 1 ))
   (( BW = BW + 1000000 ))
done


SRC_SW="ncsus1"
DST_SW="rencis1"
SRC_PORT="12"
DST_PORT="12"
((SRC_VLAN=1091))
((DST_VLAN=2091))
((BW=1000000))

for i in `seq 91 100`; do
   echo "$i  ${SRC_SW} ${DST_SW} ${SRC_PORT} ${DST_PORT} ${SRC_VLAN} ${DST_VLAN} ${BW}" >> ${FILE}
   (( SRC_VLAN = SRC_VLAN + 1 ))
   (( DST_VLAN = DST_VLAN + 1 ))
   (( BW = BW + 1000000 ))
done


SRC_SW="ncsus1"
DST_SW="dukes1"
SRC_PORT="12"
DST_PORT="12"
((SRC_VLAN=1101))
((DST_VLAN=2101))
((BW=1000000))

for i in `seq 101 110`; do
   echo "$i  ${SRC_SW} ${DST_SW} ${SRC_PORT} ${DST_PORT} ${SRC_VLAN} ${DST_VLAN} ${BW}" >> ${FILE}
   (( SRC_VLAN = SRC_VLAN + 1 ))
   (( DST_VLAN = DST_VLAN + 1 ))
   (( BW = BW + 1000000 ))
done


SRC_SW="ncsus1"
DST_SW="uncs1"
SRC_PORT="12"
DST_PORT="12"
((SRC_VLAN=1111))
((DST_VLAN=2111))
((BW=1000000))

for i in `seq 111 120`; do
   echo "$i  ${SRC_SW} ${DST_SW} ${SRC_PORT} ${DST_PORT} ${SRC_VLAN} ${DST_VLAN} ${BW}" >> ${FILE}
   (( SRC_VLAN = SRC_VLAN + 1 ))
   (( DST_VLAN = DST_VLAN + 1 ))
   (( BW = BW + 1000000 ))
done
















