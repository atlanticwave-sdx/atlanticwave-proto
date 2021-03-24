#!/bin/bash


TEMP_FILE=/tmp/trap.txt
SDX_CONTROLLER_LOCAL="0"


function clean_up {

        echo "--- ERROR" > $TEMP_FILE 2>&1
        exit
}

trap clean_up SIGHUP SIGINT SIGTERM


usage(){
    echo -e "   Usage: $0 [-s <switch>] [-b <bridge_number>] [-v <vlan-tag>] [-c <controller>] [-t <project>] [-p <physical port>] [-l <ofport>] [-o <operation>] [-i <dpid>] [-j <bridge-descr>] [-n netns] [-r resource] [-e eline_connection]  [-h]"
    echo -e "\t -s <switch> [renci|uc_1|uc_2|tacc]"
    echo -e "\t -h: Usage"
    echo
}


title(){
    echo ""
    echo "============================================================================== "
    echo "--- $1"
    echo "============================================================================== "
}


function get1
{  
   URL=$1
   curl -s -k -H "Accept: application/json" --request GET ${URL} | python -m json.tool | jq '.'
}

function get2
{  
   URL=$1
   COOKIE=$2
   curl -s -k -b ${COOKIE} -H "Accept: application/json" --request GET ${URL} | python -m json.tool | jq '.'
}

function post1
{
   URL=$1
   JSON=$2
   COOKIE=$3
   curl -k -b ${COOKIE}\
        -H "Content-Type:application/json" \
        -X POST ${URL} \
        -d ${JSON}  | python -m json.tool | jq '.'


}


get(){
   HEADER="Accept: application/json"
   URL=$1
   QUERY=$2
   if [[ -n ${QUERY} && ${QUERY} -eq 1  ]]; then
       URL="${URL}?list=true"
       curl -k -H ${HEADER} -X GET ${URL} | python -m json.tool | jq '.'
   else
       curl -k -H ${HEADER} -X GET ${URL} | python -m json.tool | jq '.'
   fi
}


delete()
{
   URL=$1
   JSON=$2
   curl -k \
        -H "Content-Type:application/json" \
        -X DELETE ${URL}
}


generate_post_data_endpointconnection(){
   DEADLINE=$1
   SRCENDPOINT=$2
   DSTENDPOINT=$3
   DATAQUANTITY=$4
   cat << EOF
{  'EndpointConnection': { 'deadline':'${DEADLINE}', 'srcendpoint':'${SRCENDPOINT}', 'dstendpoint':'${DSTENDPOINT}', 'dataquantity':${DATAQUANTITY} } }
EOF
}


generate_post_data_l2multipoint(){
   STARTTIME=$1
   ENDTIME=$2
   BANDWIDTH=$3
   ENDPOINT1=$4
   ENDPOINT2=$5
   ENDPOINT3=$6

   IFS=':' read -ra E1 <<< "$ENDPOINT1"  
   IFS=':' read -ra E2 <<< "$ENDPOINT2"  
   IFS=':' read -ra E3 <<< "$ENDPOINT3"  
   
   cat << EOF
{'L2Tunnel':{"starttime":"${STARTTIME}", "endtime":"${ENDTIME}", "endpoints":[ { "switch":"${E1[0]}", "port":"${E1[1]}", "vlan":"${E1[2]}" }, { "switch":"${E2[0]}", "port":"${E2[1]}", "vlan":"${E2[2]}" }, { "switch":"${E3[0]}", "port":"${E3[1]}", "vlan":"${E3[2]}" } ], "bandwidth":"${BANDWIDTH}"}}
EOF
}



generate_post_data_l2tunnel(){
   STARTTIME=$1
   ENDTIME=$2
   BANDWIDTH=$3
   ENDPOINT1=$4
   ENDPOINT2=$5

   IFS=':' read -ra E1 <<< "$ENDPOINT1"  
   IFS=':' read -ra E2 <<< "$ENDPOINT2"  

   cat << EOF
{
  "L2Tunnel":{
    "starttime":"${STARTTIME}",
    "endtime":"${ENDTIME}",
    "srcswitch":"${E1[0]}",
    "dstswitch":"${E2[0]}",
    "srcport":${E1[1]},
    "dstport":${E2[1]},
    "srcvlan":${E1[2]},
    "dstvlan":${E2[2]},
    "bandwidth":${BANDWIDTH}
  }
}
EOF
}


while getopts "o:c:t:s:d:q:1:2:3:a:b:w:L:S:P:N:U:Xh" opt; do
    case $opt in
        o)
            OPERATION=$OPTARG
            ;;
        c)
            COOKIE=$OPTARG
            ;;
        t)
            DEADLINE=$OPTARG
            ;;
        s)
            SRCENDPOINT=$OPTARG
            ;;
        d)
            DSTENDPOINT=$OPTARG
            ;;
        q)
            DATAQUANTITY=$OPTARG
            ;;
        1)
            ENDPOINT1=$OPTARG
            ;;
        2)
            ENDPOINT2=$OPTARG
            ;;
        3)
            ENDPOINT3=$OPTARG
            ;;
        a)
            STARTTIME=$OPTARG
            ;;
        b)
            ENDTIME=$OPTARG
            ;;
        w)
            BANDWIDTH=$OPTARG
            ;;
        L)
            LC=$OPTARG
            ;;
        S)
            SWITCH=$OPTARG
            ;;
        P)
            PORT=$OPTARG
            ;;
        N)
            POLICYNUMBER=$OPTARG
            ;;
        U)
            URL_INFO=$OPTARG
            ;;
        X)
            SDX_CONTROLLER_LOCAL="1"
            ;;
        h)
            usage
            clean_up
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            clean_up
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            usage
            clean_up
            ;;
    esac
done


HEADER="Accept: application/json"

endpoint='api/v1'

ep_localcontrollers="${endpoint}/localcontrollers"    # Local Controllers
ep_users="${endpoint}/users"                          # Users
ep_policies="${endpoint}/policies"                    # Policies


ep_policies_endpointconnection="${ep_policies}/type/EndpointConnection"
ep_policies_l2multipoint="${ep_policies}/type/L2Multipoint"
ep_policies_l2tunnel="${ep_policies}/type/L2Tunnel"

ep_localcontrollers_lc="${ep_localcontrollers}/${LC}"
ep_localcontrollers_lc_internalconfig="${ep_localcontrollers_lc}/internalconfig"
ep_localcontrollers_lc_switches="${ep_localcontrollers_lc}/switches"
ep_localcontrollers_lc_switch_x="${ep_localcontrollers_lc_switches}/${SWITCH}"
ep_localcontrollers_lc_switch_ports="${ep_localcontrollers_lc_switch_x}/ports"
ep_localcontrollers_lc_switch_port_x="${ep_localcontrollers_lc_switch_ports}/${PORT}"

ep_policies_type="${ep_policies}/type"
ep_policies_x="${ep_policies}/number/${POLICYNUMBER}"





protocol_http="http://"
sdx_controller_ip="192.168.201.156"
sdx_controller_dns="atlanticwave-sdx-controller.renci.ben"
sdx_controller_localhost="127.0.0.1"



sdx_controller_port="5000"
if [ ${SDX_CONTROLLER_LOCAL} == "1" ]; then
   sdx_controller="${protocol_http}${sdx_controller_localhost}:${sdx_controller_port}"
else
   sdx_controller="${protocol_http}${sdx_controller_dns}:${sdx_controller_port}"
fi


URL_ENDPOINTCONNECTION="${sdx_controller}/${ep_policies_endpointconnection}"
URL_L2MULTIPOINT="${sdx_controller}/${ep_policies_l2multipoint}"
URL_L2TUNNEL="${sdx_controller}/${ep_policies_l2tunnel}"

URL_ALL_LC="${sdx_controller}/${ep_localcontrollers}"
URL_LC="${sdx_controller}/${ep_localcontrollers_lc}"
URL_LC_INTERNALCONFIG="${sdx_controller}/${ep_localcontrollers_lc_internalconfig}"
URL_LC_SWITCHES="${sdx_controller}/${ep_localcontrollers_lc_switches}"
URL_LC_SWITCH="${sdx_controller}/${ep_localcontrollers_lc_switch_x}"
URL_LC_SWITCH_PORTS="${sdx_controller}/${ep_localcontrollers_lc_switch_ports}"
URL_LC_SWITCH_PORT="${sdx_controller}/${ep_localcontrollers_lc_switch_port_x}"

URL_POLICIES="${sdx_controller}/${ep_policies}"
URL_POLICY_TYPE="${sdx_controller}/${ep_policies_type}"
URL_POLICY_X="${sdx_controller}/${ep_policies_x}"



case ${OPERATION} in
    get_localcontrollers)
                   title "Get all  bridge information - ${URL_ALL_LC}"
                   get1 ${URL_ALL_LC}
                   ;;

    get_lc)
                   title "Get LC - ${URL_LC}"
                   get1 ${URL_LC}
                   ;;

    get_lc_internalconfig)
                   title "Get LC - ${URL_LC_INTERNALCONFIG}"
                   get2 ${URL_LC_INTERNALCONFIG} ${COOKIE}
                   ;;

    get_lc_switches)
                   title "Get LC - ${URL_LC_SWITCHES}"
                   get2 ${URL_LC_SWITCHES} ${COOKIE}
                   ;;
    get_lc_switch)
                   title "Get LC - ${URL_LC_SWITCH}"
                   get2 ${URL_LC_SWITCH} ${COOKIE}
                   ;;
    get_lc_switch_ports)
                   title "Get LC - ${URL_LC_SWITCH_PORTS}"
                   get2 ${URL_LC_SWITCH_PORTS} ${COOKIE}
                   ;;
  
    get_lc_switch_port)
                   title "Get LC - ${URL_LC_SWITCH_PORT}"
                   get2 ${URL_LC_SWITCH_PORT} ${COOKIE}
                   ;;
    get_policies)
                   title "Get POLICY - ${URL_POLICIES}"
                   get2 ${URL_POLICIES} ${COOKIE}
                   ;;
  
    get_policy_type)
                   title "Get POLICY - ${URL_POLICY_TYPE}"
                   get2 ${URL_POLICY_TYPE} ${COOKIE}
                   ;;
    get_policy)
                   title "Get POLICY - ${URL_POLICY_X}"
                   get2 ${URL_POLICY_X} ${COOKIE}
                   ;;
    get_info)
                   title "Get INFO - ${URL_INFO} "
                   get2 ${URL_INFO} ${COOKIE}
                   ;;
  
    create_endpointconnection)
                   title "ENDPOINTCONNECTION Create => Deadline: ${DEADLINE} - Srcendpoint: ${SRCENDPOINT} - Dstendpoint: ${DSTENDPOINT} - Dataquantity: ${DATAQUANTITY}"
                   DATA=$(generate_post_data_endpointconnection ${DEADLINE} ${SRCENDPOINT} ${DSTENDPOINT} ${DATAQUANTITY})
                   echo -e "--- DATA: \n${DATA}"
                   curl -k -s \
                        -b ${COOKIE} \
                        -H "Content-Type: application/json"\
                        -X POST ${URL_ENDPOINTCONNECTION} \
                        -d "$( generate_post_data_endpointconnection ${DEADLINE} ${SRCENDPOINT} ${DSTENDPOINT} ${DATAQUANTITY} )" | python -m json.tool | jq '.'
                   ;;
    create_l2tunnel)
                   title "L2TUNNEL Create => STARTIME: ${STARTTIME} - ENDTIME: ${ENDTIME} - BW: ${BANDWIDTH} - EP1: ${ENDPOINT1} - EP2: ${ENDPOINT2}"
                   DATA=$(generate_post_data_l2tunnel  ${STARTTIME} ${ENDTIME} ${BANDWIDTH} ${ENDPOINT1} ${ENDPOINT2})
                   echo -e "--- DATA: \n${DATA}"
                   curl -k -s \
                        -b ${COOKIE} \
                        -H "Content-Type: application/json"\
                        -X POST ${URL_ENDPOINTCONNECTION} \
                        -d "$( generate_post_data_l2tunnel ${STARTTIME} ${ENDTIME} ${BANDWIDTH} ${ENDPOINT1} ${ENDPOINT2} )" | python -m json.tool | jq '.'
                   ;;

    create_ep1)
                   JSON="'{\"EndpointConnection\":{\"deadline\":\"2018-21-12T23:59:59\",\"srcendpoint\":\"rencidtn\",\"dstendpoint\":\"dukedtn\",\"dataquantity\":800000000}}'"
                   title "${JSON}"
                   post1 ${URL_ENDPOINTCONNECTION} ${JSON} ${COOKIE}
                   ;;
esac

