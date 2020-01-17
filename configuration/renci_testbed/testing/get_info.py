#!/usr/bin/env python 

#import logging
import requests
import json
import sdxrest
import sys
import time
import re
import os
import cookielib

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

header_sdx = {"Accept": "application/json"}
cookie = os.path.abspath("/root/cookie/awcookie.txt")

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


title('GET LOCAL CONTROLLERS')
A = sdxrest.get_localcontrollers(header_sdx, sdx_controller)
print(json.dumps(A.json(), indent=4, sort_keys=True))


title('GET LOCAL CONTROLLER - RENCI')
lc = "rencictlr"
A = sdxrest.get_localcontroller(header_sdx, sdx_controller, lc )
print(json.dumps(A.json(), indent=4, sort_keys=True))

title('GET LOCAL CONTROLLER - DUKE')
lc = "dukectlr"
A = sdxrest.get_localcontroller(header_sdx, sdx_controller, lc )
print(json.dumps(A.json(), indent=4, sort_keys=True))

title('GET LOCAL CONTROLLER - UNC')
lc = "uncctlr"
A = sdxrest.get_localcontroller(header_sdx, sdx_controller, lc )
print(json.dumps(A.json(), indent=4, sort_keys=True))

title('GET LOCAL CONTROLLER - NCSU')
lc = "ncsuctlr"
A = sdxrest.get_localcontroller(header_sdx, sdx_controller, lc )
print(json.dumps(A.json(), indent=4, sort_keys=True))


title('GET INTERNALCONFIG on LOCAL CONTROLLER - RENCI')
lc = "rencictlr"
cj = cookielib.MozillaCookieJar('awcookie.txt')
cj.load()
print len(cj)
for cookie in cj:
    # set cookie expire date to 14 days from now
    cookie.expires = time.time() + 14 * 24 * 3600

    A = sdxrest.get_localcontroller_internalconfig(header_sdx, sdx_controller, lc, cookie=cookie )
    print(json.dumps(A.json(), indent=4, sort_keys=True))


title('GET SWITCHES associated with LOCAL CONTROLLER - RENCI')
lc = "rencictlr"
A = sdxrest.get_localcontroller_switches(header_sdx, sdx_controller, lc )
print(json.dumps(A.json(), indent=4, sort_keys=True))


title('GET SWITCH RENCIS1')
lc = "rencictlr"
switch = "rencis1"
A = sdxrest.get_localcontroller_switch(header_sdx, sdx_controller, lc, switch)
print(json.dumps(A.json(), indent=4, sort_keys=True))


title('GET SWITCH RENCIS1 PORTS')
lc = "rencictlr"
switch = "rencis1"
A = sdxrest.get_localcontroller_switch_ports(header_sdx, sdx_controller, lc, switch)
print(json.dumps(A.json(), indent=4, sort_keys=True))


title('GET SWITCH RENCIS1 PORT 1')
lc = "rencictlr"
switch = "rencis1"
port = "1"
A = sdxrest.get_localcontroller_switch_port(header_sdx, sdx_controller, lc, switch, port)
print(json.dumps(A.json(), indent=4, sort_keys=True))


title('GET USERS')
A = sdxrest.get_users(header_sdx, sdx_controller)
print(json.dumps(A.json(), indent=4, sort_keys=True))


title('GET USERS')
user="mcevik"
A = sdxrest.get_user(header_sdx, sdx_controller,user)
print(json.dumps(A.json(), indent=4, sort_keys=True))


title('GET USER PERMISSIONS')
user="mcevik"
A = sdxrest.get_user_permissions(header_sdx, sdx_controller,user)
print(json.dumps(A.json(), indent=4, sort_keys=True))


title('GET USER POLICIES')
user="mcevik"
A = sdxrest.get_user_policies(header_sdx, sdx_controller,user)
print(json.dumps(A.json(), indent=4, sort_keys=True))


title('GET SDX POLICIES')
A = sdxrest.get_policies(header_sdx, sdx_controller)
print(json.dumps(A.json(), indent=4, sort_keys=True))


title('GET SDX POLICIES')
A = sdxrest.get_policies(header_sdx, sdx_controller)
print(json.dumps(A.json(), indent=4, sort_keys=True))





