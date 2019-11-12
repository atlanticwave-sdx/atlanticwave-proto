# Copyright 2019 - Sean Donovan
# AtlanticWave/SDX Project

# This is an example Science Gateway-like application that creates paths and 
# initiates transfers between our pseudo-DTN applications


import sys
import subprocess
from datetime import datetime, timedelta
from time import sleep


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

# List of endpoints
endpoints = {'atl-dtn':{'ip':'1.2.3.4','port':9999, 
                        'switch':'atl-switch', 'switchport':3, 'vlan':123},
             'mia-dtn':{'ip':'2.3.4.5','port':9999,
                        'switch':'mia-switch', 'switchport':2, 'vlan':123}}

global sdx_ip, sdx_port, sdx_user, sdx_pw, login_cookie, tunnel_policy
sdx_ip = '1.2.3.4'
sdx_port = 5555
sdx_user = 'sdonovan'
sdx_pw = '1234'
login_cookie = None
tunnel_policy = None


def create_tunnel(srcswitch, dstswitch, srcport, dstport, 
                  srcvlan, dstvlan, time):
    global sdx_ip, sdx_port, login_cookie, tunnel_policy
    
    rfc3339format = "%Y-%m-%dT%H:%M:%S"


    if login_cookie == None:
        login_to_sdx_controller()

    # Calculate start and end times
    starttime = datetime.now()
    endtime = starttime + time

    # Issue POST command
    endpoint = "http://%s:%s/api/v1/policies/type/l2tunnel" % (sdx_ip, sdx_port)
    l2tunnel = '{"L2Tunnel":{"starttime":"%s","endtime":"%s","srcswitch":"%s","dstswitch":"%s","srcport":%s,"dstport":%s,"srcvlan":%s,"dstvlan":%s,"bandwidth":10000000}}' % (
        starttime.strftime(rfc3339format), endtime.strftime(rfc3339format), 
        srcswitch, dstswitch, srcport, dstport, srcvlan, dstvlan)
        
    output = subprocess.check_call(['curl', '-X', 'POST',
                                    '-H',
                                    'Content-type: application/json',
                                    '-H', "Accept: application/json",
                                    endpoint,
                                    '-d', l2tunnel,
                                    '-b', login_cookie])

    # Get policy number
    output = json.loads(output)
    installed_policynum = int(output['policy']['href'].split('/')[-1])
    
    # Set tunnel_policy 
    tunnel_policy = installed_policynum

def delete_tunnel():
    global sdx_ip, sdx_port, tunnel_policy, login_cookie

    if login_cookie == None:
        login_to_sdx_controller()

    # Issue DELETE command
    endpoint = "http://%s:%s/api/vl/policies/number/%s" % (
       sdx_ip, sdx_port, tunnel_policy)

    output = subprocess.check_call(['curl', '-X', 'DELETE',
                                    '-H', 'Accept: application/json',
                                    endpoint,
                                    '-b' login_cookie])

    tunnel_policy = None

def login_to_sdx_controller():
    global sdx_ip, sdx_port, sdx_user, sdx_pw, login_cookie
    
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
    for ep in endpoints:
        if a == num:
            return endpoinep

def get_dir(srcip, srcport):
    endpoint = 'http://%s:%s/dtn/transfer/%s' % (srcip, srcport, srcip)
    output = subprocess.check_output(['curl', '-X', 'GET', endpoint])

    

def parse_files(filestr):
    # Split the filestr into a list of files
    # Based on https://stackoverflow.com/questions/1894269/convert-string-representation-of-list-to-list
    ls = filestr.strip('[]').replace('"', '').replace(' ', '').split(',')
    return ls


def print_files(files):
    a = 0
    for f in files:
        print("%s - %s" % (a, f))
        a += 1


def transfer_file(srcip, srcport, dstip, dstport, filename):
    timeout = 1000

    # Execute file transfer
    endpoint = 'http://%s:%s/dtn/transfer/%s/%s' % (
        dstip, dstport, srcip, filename)
    output = subprocess.check_output(['curl', '-X', 'POST', endpoint])
    print("Transferring file: %s" % output)

    # loop here, checking on status
    endpoint = 'http://%s:%s/dtn/status' % (dstip, dstport)

    output =''
    count = 0
    while('Started Transfer' in output):
        output = subprocess.check_output(['curl', '-X', 'GET', endpoint])
        sleep(1)
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
    srcdict = get_ep_dict_from_num(endpoints, src)
    dstdict = get_ep_dict_from_num(endpoints, dst)
    
    create_tunnel(srcdict['switch'],     dstdict['switch'],
                  srcdict['switchport'], dstdict['switchport'], 
                  srcdict['vlan'],       dstdict['vlan'],
                  timedelta(0,1))

    # Get and display files available on src
    rawfiles = get_dir(srcdict['ip'], srcdict['port'])
    fileslist = parse_files(rawfiles)
    print_files(fileslist)
    delete_tunnel()

    # Let user choose file to transfer
    filenumber = input("Choose a file: ")
    filename = fileslist[filenumber]

    # Reestablish path between src and dest
    create_tunnel(srcdict['switch'],     dstdict['switch'],
                  srcdict['switchport'], dstdict['switchport'],
                  srcdict['vlan'],       dstdict['vlan'],
                  timedelta(1,0)) # 1 day, excessive, but we'll delete it, don't worry

    # Make transfer call
    transfer_file(srcdict['ip'], srcdict['port'],
                  dstdict['ip'], dstdict['port'], filename)    

    # Clean up
    delete_tunnel()
