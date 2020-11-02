#!/usr/bin/env python 

#import logging
import requests
import json
import sdxrest
import sys
import time
import re

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

header_sdx = {"Accept": "application/json"}

protocol_https = 'https://'
protocol_http = 'http://'
sdx_controller_ip = '192.168.201.156'
sdx_controller_port = '5000'
sdx_controller = protocol_http + sdx_controller_ip + ':' + sdx_controller_port

def title(text):
   print ("----------------------------------------------------")
   print (text)
   print ("----------------------------------------------------")


#url="http://192.168.201.156:5000/api/v1/localcontrollers"
#url="http://192.168.201.156:5000/api/v1/localcontrollers/ncsuctlr/internalconfig"

#title('LOCAL CONTROLLERS - InternalConfig')
#A = sdxrest.get_info(headers=header_sdx,info_url=url)
#print(json.dumps(A.json(), indent=4, sort_keys=True))


title('-----')

#(u'6', {'EndpointConnection': {'dstendpoint': u'rencidtn', 'srcendpoint': u'rencibm4', 'dataquantity': 1000000000, 'deadline': u'2018-12-24T23:59:00'}}, 'EndpointConnection', 'ACTIVE RULE', u'mcevik', ['rencictlr:VlanTunnelLCRule: switch 205, 6:4:23:1425:1:True:20662', 'rencictlr:VlanTunnelLCRule: switch 201, 6:12:23:1421:1:True:20662'])

deadline='2018-12-24T23:59:00'
srcendpoint='rencidtn'
dstendpoint='uncdtn'
dataquantity='1000000000'

A = sdxrest.post_policy_type_endpoint(header_sdx, sdx_controller, deadline, srcendpoint, dstendpoint, dataquantity)
print(json.dumps(A.json(), indent=4, sort_keys=True))

