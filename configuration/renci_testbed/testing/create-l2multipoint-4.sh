#!/bin/bash


PWD=`pwd`
FILE="${PWD}/config_file_l2multipoint_4.txt"

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

#for i in ${a50[@]}; do 
for i in `seq 1 100`; do 

#   echo "--- SEQ = $i"
#   echo "--- DATE = `date`"
   LINE=`cat ${FILE} | grep -w ^${i}`
   echo $LINE

   EP1=`echo $LINE | awk '{print $2}'`
   EP2=`echo $LINE | awk '{print $3}'`
   EP3=`echo $LINE | awk '{print $4}'`
   EP4=`echo $LINE | awk '{print $5}'`
   EP1_PORT=`echo $LINE | awk '{print $6}'`
   EP2_PORT=`echo $LINE | awk '{print $7}'`
   EP3_PORT=`echo $LINE | awk '{print $8}'`
   EP4_PORT=`echo $LINE | awk '{print $9}'`
   EP1_VLAN=`echo $LINE | awk '{print $10}'`
   EP2_VLAN=`echo $LINE | awk '{print $11}'`
   EP3_VLAN=`echo $LINE | awk '{print $12}'`
   EP4_VLAN=`echo $LINE | awk '{print $13}'`
   BW=`echo $LINE | awk '{print $14}'`


   printf -v data '{"L2Multipoint":{"starttime":"2019-03-26T12:00:00","endtime":"2019-04-15T23:59:00","endpoints":[{"switch":"%s","port":%i,"vlan":%i},{"switch":"%s","port":%i,"vlan":%i},{"switch":"%s","port":%i,"vlan":%i},{"switch":"%s","port":%i,"vlan":%i}],"bandwidth":%i}}' ${EP1} ${EP1_PORT} ${EP1_VLAN} ${EP2} ${EP2_PORT} ${EP2_VLAN} ${EP3} ${EP3_PORT} ${EP3_VLAN} ${EP4} ${EP4_PORT} ${EP4_VLAN} ${BW}
   echo "--- DATA: $data"
   curl -s -X POST http://127.0.0.1:5000/api/v1/policies/type/L2Multipoint -b aw1.cookie -H "Content-Type: application/json" -d "$data"
   #sleep 1
   echo " "
   echo " "
#   echo " "
#   echo " "
#   echo " "
 
done
