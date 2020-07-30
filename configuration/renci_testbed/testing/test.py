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


url="http://192.168.201.156:5000/api/v1/login"
#A = sdxrest.get_info(headers=header_sdx,info_url=url)
#print A.status_code
#print A.content


def save_cookies(requests_cookiejar, filename):
    with open(filename, 'wb') as f:
        pickle.dump(requests_cookiejar, f)

def load_cookies(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)
filename = 'file.txt'
#save cookies
r = requests.get(url)
save_cookies(r.cookies, filename)

#load cookies and do a request
requests.get(url, cookies=load_cookies(filename))

