#!/bin/bash


PWD=`pwd`
FILE="${PWD}/config_file.txt"

MIN=1
MAX=120
DIFF=$(($MAX-$MIN+1))
RANDOM=$$
NUMARRAY20=""
NUMARRAY50=""
NUMARRAY100=""

for i in `seq 1 25`; do
   R=$(($(($RANDOM%$DIFF))+$MIN))
   NUM_ARRAY20[$i]=$R
done

for i in `seq 1 75`; do
   R=$(($(($RANDOM%$DIFF))+$MIN))
   NUM_ARRAY50[$i]=$R
done
  
for i in `seq 1 120`; do
   R=$(($(($RANDOM%$DIFF))+$MIN))
   NUM_ARRAY100[$i]=$R
done

eval a20=($(printf "%q\n" "${NUM_ARRAY20[@]}" | sort -u))
eval a50=($(printf "%q\n" "${NUM_ARRAY50[@]}" | sort -u))
eval a100=($(printf "%q\n" "${NUM_ARRAY100[@]}" | sort -u))

echo "--- NUMBERS: ${a50[@]}" 

for i in ${a50[@]}; do 
#for i in `seq 91 120`; do 

#   echo "--- SEQ = $i"
#   echo "--- DATE = `date`"
   LINE=`cat ${FILE} | grep -w ^${i}`
   echo $LINE

   SRC_SW=`echo $LINE | awk '{print $2}'`
   DST_SW=`echo $LINE | awk '{print $3}'`
   SRC_PORT=`echo $LINE | awk '{print $4}'`
   DST_PORT=`echo $LINE | awk '{print $5}'`
   SRC_VLAN=`echo $LINE | awk '{print $6}'`
   DST_VLAN=`echo $LINE | awk '{print $7}'`
   BW=`echo $LINE | awk '{print $8}'`

   printf -v data '{"L2Tunnel":{"starttime":"2019-02-14T12:00:00","endtime":"2019-02-20T23:59:00","srcswitch":"%s","dstswitch":"%s","srcport":12,"dstport":12,"srcvlan":%i,"dstvlan":%i,"bandwidth":%i}}' ${SRC_SW} ${DST_SW} ${SRC_VLAN} ${DST_VLAN} ${BW}

#   echo "--- DATA: $data"
   curl -s -X POST http://127.0.0.1:5000/api/v1/policies/type/L2Tunnel -b aw1.cookie -H "Content-Type: application/json" -d "$data"
#   echo " "
#   echo " "
#   echo " "
#   echo " "
#   echo " "
 
done
