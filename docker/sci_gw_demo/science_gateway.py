# Copyright 2019 - Sean Donovan
# AtlanticWave/SDX Project

# This is an example Science Gateway-like application that creates paths and 
# initiates transfers between our pseudo-DTN applications


import sys
import subprocess
from datetime import datetime, timedelta
from time import sleep
import json

# HTTP status codes:
HTTP_GOOD           = 200
HTTP_CREATED        = 201
HTTP_ACCEPTED       = 202
HTTP_NO_CONTENT     = 204
HTTP_NOT_MODIFIED   = 304
HTTP_BAD_REQUEST    = 400
HTTP_FORBIDDEN      = 403     # RETURNED BY FLASK-RESTFUL ONLY
HTTP_NOT_FOUND      = 404
HTTP_NOT_ACCEPTABLE = 406
HTTP_CONFLICT       = 409
HTTP_SERVER_ERROR   = 500     # RETURNED BY FLASK-RESTFUL ONLY

port = 9999

TUNNEL = True
#TUNNEL = False
# List of endpoints
endpoints = {'atl-dtn':{'ctrlip':'10.100.1.21','port':9999,
                        'dataip':'10.201.2.21', 'switch':'soxswitch-216-3', 
                        'switchport':4, 'vlan':201},
             'mia-dtn':{'ctrlip':'10.100.1.27','port':9999,
                        'dataip':'10.201.2.28', 'switch':'miaswitch-206-198', 
                        'switchport':10, 'vlan':124}}

global sdx_ip, sdx_port, sdx_user, sdx_pw, login_cookie, tunnel_policy
sdx_ip = '10.100.1.21'
sdx_port = 5000
sdx_user = 'sdonovan'
sdx_pw = '1234'
login_cookie = None
tunnel_policy = None


def create_tunnel(srcswitch, dstswitch, srcport, dstport, 
                  srcvlan, dstvlan, time):
    global sdx_ip, sdx_port, login_cookie, tunnel_policy
    
    rfc3339format = "%Y-%m-%dT%H:%M:%S"
    print("Creating tunnel from %s:%s:%s to %s:%s:%s for %s time." % (
        srcswitch, srcport, srcvlan, dstswitch, dstport, dstvlan, time))

    if login_cookie == None:
        login_to_sdx_controller()

    # Calculate start and end times
    #starttime = datetime.now() - time
    #endtime = starttime + time
    # Hardwiring these, so that this will always be installable
    starttime = datetime(1999, 01, 01)
    endtime =  datetime(2030, 01, 01)

    # Issue POST command 
    endpoint = "http://%s:%s/api/v1/policies/type/L2Tunnel" % (sdx_ip, sdx_port)
    l2tunnel = '{"L2Tunnel":{"starttime":"%s","endtime":"%s","srcswitch":"%s","dstswitch":"%s","srcport":%s,"dstport":%s,"srcvlan":%s,"dstvlan":%s,"bandwidth":10000000}}' % (
        starttime.strftime(rfc3339format), endtime.strftime(rfc3339format), 
        srcswitch, dstswitch, srcport, dstport, srcvlan, dstvlan)
        
    output = subprocess.check_output(['curl', '-X', 'POST',
                                    '-H',
                                    'Content-type: application/json',
                                    '-H', "Accept: application/json",
                                    endpoint,
                                    '-d', l2tunnel,
                                    '-b', login_cookie])

    # Get policy number
    print("OUTPUT: %s" % output)
    output = json.loads(output.decode('utf-8'))
    installed_policynum = int(output['policy']['href'].split('/')[-1])
    
    # Set tunnel_policy 
    tunnel_policy = installed_policynum

    sleep(3)

def delete_tunnel():
    global sdx_ip, sdx_port, tunnel_policy, login_cookie

    if login_cookie == None:
        login_to_sdx_controller()

    # Issue DELETE command
    print("Deleting policy #%s" % tunnel_policy)

    endpoint = "http://%s:%s/api/v1/policies/number/%s" % (
       sdx_ip, sdx_port, tunnel_policy)

    print("Deleting policy endpoint %s" % endpoint)

    output = subprocess.check_call(['curl', '-X', 'DELETE',
                                    '-H', 'Accept: application/json',
                                    endpoint,
                                    '-b', login_cookie])

    tunnel_policy = None

def login_to_sdx_controller():
    global sdx_ip, sdx_port, sdx_user, sdx_pw, login_cookie
    
    print("Logging into SDX Controller: %s:%s - %s:%s" % (
        sdx_ip, sdx_port, sdx_user, sdx_pw))
    # if there's a saved login, return
    if login_cookie != None:
        return

    # Login to SDX Controller
    cookie_filename = 'sdx.cookie'
    endpoint = 'http://%s:%s/api/v1/login' % (sdx_ip, sdx_port)
    output = subprocess.check_output(['curl', '-X', 'POST',
                                      '-F', 'username=%s'%sdx_user,
                                      '-F', 'password=%s'%sdx_pw,
                                      endpoint, 
                                      '-c', cookie_filename])

    # set login_cookie to the filename
    login_cookie = cookie_filename
    print("Logged into SDX Controller %s:%s" % (sdx_ip, sdx_port))


def print_endpoint(endpoints):
    a = 0
    for ep in endpoints:
        print("%s - %s" % (a, ep))
        a += 1

def get_ep_dict_from_num(endpoints, num):
    a = 0
    for ep in endpoints.keys():
        if a == num:
            return endpoints[ep]
        a += 1

def get_dir(ctrlip, dataip, srcport):
    print("Getting directory info for %s:%s:%s" % (
        ctrlip, dataip, srcport))
    endpoint = 'http://%s:%s/dtn/transfer/%s' % (ctrlip, srcport, dataip)
    print("    %s"% endpoint)
    output = subprocess.check_output(['curl', '-X', 'GET', endpoint])
    return output.decode('utf-8')
    

def parse_files(filestr):
    print("Parsing files")
    # Split the filestr into a list of files
    # Based on https://stackoverflow.com/questions/1894269/convert-string-representation-of-list-to-list
    ls = filestr.strip('[]').replace('[','').replace(']','').replace('"', '').replace("'", '').replace(' ', '').split(',')
    return ls


def print_files(files):
    a = 0
    for f in files:
        print("%s - %s" % (a, f))
        a += 1


def transfer_file(srcdataip, dstctrlip, dstport, filename):
    print("Trying to transfer file %s from %s to %s:%s" % (
        filename, srcdataip, dstctrlip, dstport))
    timeout = 1000

    # Execute file transfer
    endpoint = 'http://%s:%s/dtn/transfer/%s/%s' % (
        dstctrlip, dstport, srcdataip, filename)
    print("    %s" % endpoint)
    output = subprocess.check_output(['curl', '-X', 'POST', endpoint])
    output = output.decode('utf-8')
    print("Transferring file: %s" % output)

    # loop here, checking on status
    endpoint = 'http://%s:%s/dtn/status' % (dstctrlip, dstport)

    count = 0
    while(('Started transfer' in output) or
          ('Started Transfer' in output)):
        sleep(1)
        output = subprocess.check_output(['curl', '-X', 'GET', endpoint])
        output = output.decode('utf-8')
        print("Loop %s: %s" % (count, output))
        count += 1
        if count > timeout: break

    print("Status of transfer: %s" % output)
    if count > timeout:
        print("Transfer timed out!")
        
    # Once we have a complete or a failure, return status
    return output

# Main loop!
while(True):
    # Select src and destination
    print_endpoint(endpoints)
    src = input("Source: ")
    dst = input("Destination: ")
    
    # Establish a path between src and dst for 1 sec
    srcdict = get_ep_dict_from_num(endpoints, int(src))
    dstdict = get_ep_dict_from_num(endpoints, int(dst))

    #print("srcdict - %s" % srcdict)
    #print("dstdict - %s" % dstdict)

    if TUNNEL:
        create_tunnel(srcdict['switch'],     dstdict['switch'],
                      srcdict['switchport'], dstdict['switchport'], 
                      srcdict['vlan'],       dstdict['vlan'],
                      timedelta(100,))

    # Get and display files available on src
    rawfiles = get_dir(dstdict['ctrlip'], srcdict['dataip'], dstdict['port'])
    fileslist = parse_files(rawfiles)
    print_files(fileslist)
    if TUNNEL:
        delete_tunnel()

    # Let user choose file to transfer
    filenumber = input("Choose a file: ")
    filename = fileslist[int(filenumber)]

    # Reestablish path between src and dest
    if TUNNEL:
        create_tunnel(srcdict['switch'],     dstdict['switch'],
                      srcdict['switchport'], dstdict['switchport'],
                      srcdict['vlan'],       dstdict['vlan'],
                      timedelta(100,0)) # 1 day, excessive, but we'll delete it, don't worry

    # Make transfer call
    transfer_file(srcdict['dataip'], dstdict['ctrlip'], dstdict['port'], filename)    

    # Clean up
    if TUNNEL:
        delete_tunnel()
