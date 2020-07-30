#!/bin/bash


TEMP_FILE=/tmp/trap.txt


function clean_up {

        echo "--- ERROR" > $TEMP_FILE 2>&1
        exit
}

trap clean_up SIGHUP SIGINT SIGTERM


usage(){
    echo -e "   Usage: $0 [-s <switch>] [-b <bridge_number>] [-v <vlan-tag>] [-c <controller>] [-t <project>] [-p <physical port>] [-l <ofport>] [-o <operation>] [-i <dpid>] [-j <bridge-descr>] [-n netns] [-r resource] [-e eline_connection]  [-h]"
    echo -e "\t -s <switch> [renci|uc_1|uc_2|tacc]"
    echo -e "\t -b <bridge_number> [1 .. 63]"
    echo -e "\t -v <vlan-tag>"
    echo -e "\t -c <controller ip address>"
    echo -e "\t -t <openstack project id>"
    echo -e "\t -p <physical port>"
    echo -e "\t -l <openflow port>"
    echo -e "\t -o <operation>"
    echo -e "\t -i <dpid>"
    echo -e "\t -j <bridge-descr>"
    echo -e "\t -n <netns>"
    echo -e "\t -r <resource>"
    echo -e "\t -e <eline_connection>"
    echo -e "\t -h: Usage"
    echo
}


title(){
    echo ""
    echo "============================================================================== "
    echo "--- $1"
    echo "============================================================================== "
}


SW_UC_1="172.30.0.4"
SW_UC_2="172.30.0.5"
SW_RENCI_1="192.168.201.169"
SW_TACC_1="roc-ax35-sw1.net.tacc.utexas.edu"

SW_RENCI_2="192.168.201.168"
SW_DUKE_1="192.168.202.30"
SW_UNC_1="192.168.203.30"
SW_NCSU_1="192.168.204.30"

TOKEN_RENCI_1="245c25eac968cb22624438f0e1bcd2d766be666843676e413b6739d86f6c3523bf7aab1e5c3231aa2d7acd6757371dea3d8cbc470a1e60825f93a85dabd01ddb"
TOKEN_RENCI_2="ddc60638fa7a7aa3fb5ca10de8f4e5e8bf82cd289187f933cfc7d7a01e7f7f3839ecac1145bc9908abfd03aa493e4acda448522b304a6ce779f82ce9f1528356"
TOKEN_DUKE_1="c73ad6e29773582187c06a1558f8ecc71ea273b3a5ae9e4f03f153d73f6436a619f3c8471205c28e25f9ae62741d5435e54c8a6f33f2b333154430448dd18215"
TOKEN_UNC_1="fa18b3d4d84507dba6568678a45fcecdec03247d7b5c18e45c5f288066a52d970cf8ee0bcf7759c698a7b56b92824963c8c03acf77f0a3aa91ad4f64c3aa7b15"
TOKEN_NCSU_1="9b95dda0314beb7acf620084dff53e5df7eaf80f9ee453cfb3550f33aecd356561fcf22568ac8365f2892725f129147ceb5718cb711c3a93b136030348dd9eeb"

PROJECT=""
VLAN=""
SWITCH=""
CONTROLLER_IP=""
CONTROLLER_PORT=""
BRIDGE=""
OPERATION=""
PHYSPORT=""
OFPORT=""
DPID=""
BR_DESC=""
NETNS=""
RESOURCE=""


while getopts "s:b:v:c:k:t:p:l:o:i:j:n:r:e:h" opt; do
    case $opt in
        s)
            SWITCH=$OPTARG
            ;;
        b) 
            BRIDGE_NUM=$OPTARG
            BRIDGE="br${BRIDGE_NUM}"
            ;;
        v) 
            VLAN=$OPTARG
            ;;
        c) 
            CONTROLLER_IP=$OPTARG
            ;;
        k)
            CONTROLLER_PORT=$OPTARG
            ;;
        t) 
            PROJECT=$OPTARG
            ;;
        p) 
            PHYSPORT=$OPTARG
            ;;
        l) 
            OFPORT=$OPTARG
            ;;
        o) 
            OPERATION=$OPTARG
            ;;
        i) 
            DPID=$OPTARG
            ;;
        j) 
            BR_DESC=$OPTARG
            ;;
        n) 
            NETNS=$OPTARG
            ;;
        r) 
            RESOURCE=$OPTARG
            ;;
        e) 
            CONN=$OPTARG
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


case ${SWITCH} in
    renci-1)
            SW=${SW_RENCI_1}
            TOKEN=${TOKEN_RENCI_1}
            ;;
    uc-1)
            SW=${SW_UC_1}
            TOKEN=${TOKEN_UC_1}
            ;;
    uc-2)
            SW=${SW_UC_2}
            TOKEN=${TOKEN_UC_2}
            ;;
    tacc)
            SW=${SW_TACC_1}
            TOKEN=${TOKEN_TACC_1}
            ;;
    renci-2)
            SW=${SW_RENCI_2}
            TOKEN=${TOKEN_RENCI_2}
            ;;
    duke-1)
            SW=${SW_DUKE_1}
            TOKEN=${TOKEN_DUKE_1}
            ;;
    unc-1)
            SW=${SW_UNC_1}
            TOKEN=${TOKEN_UNC_1}
            ;;
    ncsu-1)
            SW=${SW_NCSU_1}
            TOKEN=${TOKEN_NCSU_1}
            ;;
esac

   
AUTH_HEADER="Authorization:${TOKEN}"

EP="api/v1"
# Datapath
EP_DATAPATH="${EP}/datapath"
EP_DATAPATH_STATUS="${EP}/datapath/status"
# Bridges
EP_BRIDGES="${EP}/bridges"
# Stats
EP_STATS="${EP}/stats"
# Users
EP_USERS="${EP}/users"
# System
EP_SYSTEM="${EP}/system"
# Equipment
EP_EQUIPMENT="${EP}/equipment"
# Tunnels
EP_TUNNELS="${EP}/tunnels"
# Queue-profiles
EP_QUEUE_PROFILES="${EP}/queue-profiles"
# Ports
EP_PORTS="${EP}/ports"
# Containers
EP_CONTAINERS="${EP}/containers"
# Namespaces
EP_NETNS="${EP}/netns"

VPLS="app/vpls3/v1"
VPLS_STATUS="${VPLS}/status"

EP_ELINE="app/eline/v1"




get(){
   URL=$1
   QUERY=$2
   if [[ -n ${QUERY} && ${QUERY} -eq 1  ]]; then
       URL="${URL}?list=true"
       curl -k -H ${AUTH_HEADER} -X GET ${URL} | python -m json.tool
   else
       curl -k -H ${AUTH_HEADER} -X GET ${URL} | python -m json.tool
   fi
}


delete()
{
   URL=$1
   JSON=$2
   curl -k \
        -H "Content-Type:application/json" \
        -H $AUTH_HEADER \
        -X DELETE ${URL}
}


generate_post_data_bridge(){
   BR=$1
   NETNS=$2
   RES=$3
   DESC=$4
   cat << EOF
{
   "bridge":"${BR}",
   "subtype":"openflow",
   "netns":"${NETNS}",
   "resources":${RES},
   "bridge-descr":"${DESC}"
}
EOF
}


generate_post_data_controller(){
   DESC=$1
   IP=$2
   PORT=$3
   cat << EOF
{
   "controller":"${DESC}",
   "ip":"${IP}",
   "port":${PORT}
}
EOF
}


generate_post_data_tunnel_passthrough(){
   OFPORT=$1
   PHYSPORT=$2
   cat << EOF
{
   "ofport":${OFPORT},
   "port":"${PHYSPORT}"
}
EOF
}


generate_post_data_tunnel_ctag(){
   OFPORT=$1
   PHYSPORT=$2
   VLAN=$3
   cat << EOF
{
   "ofport":${OFPORT},
   "port":"${PHYSPORT}",
   "vlan-id":${VLAN}
}
EOF
}

generate_patch_data_bridge(){
   REPLACE_PATH=$1
   VALUE=$2
   cat << EOF
[
   {
     "op": "replace",
     "path": "/${REPLACE_PATH}",
     "value": "${VALUE}"
   }
]
EOF
}

#title "Get api information"
#URL="https://${SW}/${EP}/"
#get ${URL}

#title "Get datapath information"
#URL="https://${SW}/${EP_DATAPATH}"
#get ${URL}

#title "Get datapath status"
#URL="https://${SW}/${EP_DATAPATH_STATUS}"
#get ${URL}

URL_ALL_BRIDGES="https://${SW}/${EP_BRIDGES}"
URL_BRIDGE="https://${SW}/${EP_BRIDGES}/${BRIDGE}"
URL_BRIDGE_CONTROLLERS="https://${SW}/${EP_BRIDGES}/${BRIDGE}/controllers"
URL_BRIDGE_CONTROLLER="https://${SW}/${EP_BRIDGES}/${BRIDGE}/controllers/CONT${BRIDGE}"
URL_BRIDGE_ALL_TUNNELS="https://${SW}/${EP_BRIDGES}/${BRIDGE}/tunnels"
URL_BRIDGE_TUNNEL="https://${SW}/${EP_BRIDGES}/${BRIDGE}/tunnels/${OFPORT}"

URL_ALL_TUNNELS="https://${SW}/${EP_TUNNELS}"

URL_ELINE="http://${SW}/${EP_ELINE}"
URL_ELINE_ALL_CONNECTIONS="${URL_ELINE}/connections"
URL_ELINE_CONNECTION="${URL_ELINE_ALL_CONNECTIONS}/${CONN}"
URL_ELINE_ACTIONS="${URL_ELINE_ALL_CONNECTIONS}/actions"



case ${OPERATION} in
    list_bridges)
                   title "Get all  bridge information"
                   URL=${URL_ALL_BRIDGES}
                   get ${URL}
                   ;;
    show_bridge) 
                   title "Get bridge: ${BRIDGE} information"
                   URL=${URL_BRIDGE}
                   get ${URL}
                   ;;
    show_bridge_controller)
                   title "Get bridge: ${BRIDGE} controller information"
                   URL=${URL_BRIDGE_CONTROLLERS}
                   get ${URL}
                   title "Get bridge: ${BRIDGE} controller: CONT${BRIDGE} information"
                   get ${URL_BRIDGE_CONTROLLER}
                   ;;
    list_bridge_tunnels)
                   title "Get bridge: ${BRIDGE} tunnel information"
                   URL=${URL_BRIDGE_ALL_TUNNELS}
                   get ${URL}
                   ;;
    show_bridge_tunnel)
                   title "Get bridge: ${BRIDGE} tunnel port:${OFPORT} information"
                   URL=${URL_BRIDGE_ALL_TUNNEL}
                   get ${URL}
                   ;;
    replace_bridge_dpid)
                   title "Replace bridge: ${BRIDGE} dpid to ${DPID}"
                   curl -k -s \
                        -w "%{http_code}" \
                        -H "Content-Type:application/json" \
                        -H $AUTH_HEADER \
                        -X PATCH ${URL_BRIDGE} \
                        -d "$( generate_patch_data_bridge dpid ${DPID} )" | python -m json.tool
                   ;;
    replace_bridge_descr)
                   title "Replace bridge: ${BRIDGE} descr:${BR_DESC}"
                   curl -k -s \
                        -w "%{http_code}" \
                        -H "Content-Type:application/json" \
                        -H $AUTH_HEADER \
                        -X PATCH ${URL_BRIDGE} \
                        -d "$( generate_patch_data_bridge bridge-descr ${BR_DESC} )" | python -m json.tool
                   ;;

    tunnel_attach_passthrough)
                   title "Tunnel attach passthrough: ${BRIDGE} ofport:${OFPORT} physport: ${PHYSPORT}"
                   curl -k -s \
                        -H "Content-Type:application/json" \
                        -H $AUTH_HEADER \
                        -X POST ${URL_BRIDGE_ALL_TUNNELS} \
                        -d "$( generate_post_data_tunnel_passthrough ${OFPORT} ${PHYSPORT} )" | python -m json.tool
                   ;;
    tunnel_attach_ctag)
                   title "Tunnel attach ctag: ${BRIDGE} ofport:${OFPORT} physport: ${PHYSPORT} vlan: ${VLAN}"
                   curl -k -s \
                        -H "Content-Type:application/json" \
                        -H $AUTH_HEADER \
                        -X POST ${URL_BRIDGE_ALL_TUNNELS} \
                        -d "$( generate_post_data_tunnel_ctag ${OFPORT} ${PHYSPORT} ${VLAN} )" | python -m json.tool
                   ;;
    tunnel_detach)
                   title "Tunnel detach: ${BRIDGE} ofport:${OFPORT}"
                   delete ${URL_BRIDGE_TUNNEL}
                   ;;
    controller_add)
                   title "Controller add: ${BRIDGE} controller:${CONTROLLER_IP} ${CONTROLLER_PORT}"
                   DESC="CONT${BRIDGE}"
                   curl -k -s \
                        -H "Content-Type:application/json" \
                        -H $AUTH_HEADER \
                        -X POST ${URL_BRIDGE_CONTROLLERS} \
                        -d "$(generate_post_data_controller ${DESC} ${CONTROLLER_IP} ${CONTROLLER_PORT} )" | python -m json.tool
                   ;;
    controller_delete)
                   title "Controller delete: ${BRIDGE} controller: CONT${BRIDGE}"
                   delete ${URL_BRIDGE_CONTROLLER}
                   ;;
    bridge_create)
                   title "Bridge create: ${BRIDGE} netns: ${NETNS} resource: ${RESOURCE} descr: ${BR_DESC}"
                   DATA=$(generate_post_data_bridge ${BRIDGE} ${NETNS} ${RESOURCE} ${BR_DESC})
                   echo "--- DATA: ${DATA}"
                   curl -k -s \
                        -H "Content-Type:application/json" \
                        -H $AUTH_HEADER \
                        -X POST ${URL_ALL_BRIDGES} \
                        -d "$(generate_post_data_bridge ${BRIDGE} ${NETNS} ${RESOURCE} ${BR_DESC})" | python -m json.tool
                   ;;
    bridge_delete)
                   title "Bridge delete: ${BRIDGE} "
                   delete ${URL_BRIDGE}
                   ;;
    list_tunnels)
                   title "Get all tunnel information"
                   URL=${URL_ALL_TUNNELS}
                   get ${URL} 1
                   ;;

    show_eline)
                   title "Get eline information"
                   URL="${URL_ELINE}/"
                   get ${URL}
                   ;;
    delete_eline_connections)
                   URL="${URL_ELINE_ALL_CONNECTIONS}"
                   title "Delete eline connections: ${URL}"
                   delete ${URL}
                   ;;
    delete_eline_connection)
                   URL="${URL_ELINE_ALL_CONNECTIONS}/${CONN}"
                   title "Delete eline connections: ${URL}"
                   delete ${URL}
                   ;;
    show_eline_connections)
                   URL="${URL_ELINE_ALL_CONNECTIONS}"
                   title "Show eline connections: ${URL}"
                   get ${URL}
                   ;;
esac           

