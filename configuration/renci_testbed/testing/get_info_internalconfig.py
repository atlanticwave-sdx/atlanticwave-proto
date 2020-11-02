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
import pickle

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


title('GET INTERNALCONFIG on LOCAL CONTROLLER - RENCI')
lc = "rencictlr"
#cj = cookielib.MozillaCookieJar('awcookie.txt')
#cj.load(ignore_discard=True)
#print len(cj)
#for cookie in cj:
#    cookie.expires = time.time() + 14 * 24 * 3600
#    print str(cookie)

def load_cookies_from_lwp(filename):
    lwp_cookiejar = cookielib.LWPCookieJar()
    lwp_cookiejar.load(filename, ignore_discard=True)
    return lwp_cookiejar

A = sdxrest.get_localcontroller_internalconfig(header_sdx, sdx_controller, lc, cookie=load_cookies_from_lwp('cookie.txt'))
print(json.dumps(A.json(), indent=4, sort_keys=True))






