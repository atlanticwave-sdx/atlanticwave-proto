#!/usr/bin/env python 

import requests
import json
import re

#
# ENDPOINTS
#
endpoint = '/api/v1'

ep_localcontrollers = endpoint + '/localcontrollers'    # Local Controllers
ep_users = endpoint + '/users'    # Users
ep_policies = endpoint + '/policies'    # Policies



def title(text):
   print ("----------------------------------------------------")
   print (text)
   print ("----------------------------------------------------")




#
# GET INFO
#
#   200
#   403 Forbidden
def get_info(headers=None,
             info_url=None):

    try:
        r = requests.get(info_url, headers=headers, verify=False)
    except Exception as e:
        raise e
    return r


def get_localcontrollers(headers,
                         url_sdx_cont):
    url = url_sdx_cont + ep_localcontrollers

    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception as e:
        raise e
    return r


def get_localcontroller(headers,
                        url_sdx_cont,
                        lc):
    url = url_sdx_cont + ep_localcontrollers + '/' + str(lc)

    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception as e:
        raise e
    return r


def get_localcontroller_internalconfig(headers,
                                       url_sdx_cont,
                                       lc,
                                       cookie=None):
    url = url_sdx_cont + ep_localcontrollers + '/' + str(lc) + '/internalconfig' 

    try:
        r = requests.get(url, headers=headers, cookies=cookie, verify=False)
    except Exception as e:
        raise e
    return r


def get_localcontroller_switches(headers,
                                 url_sdx_cont,
                                 lc):
    url = url_sdx_cont + ep_localcontrollers + '/' + str(lc) + '/switches'

    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception as e:
        raise e
    return r


def get_localcontroller_switch(headers,
                               url_sdx_cont,
                               lc, 
                               switch):
    url = url_sdx_cont + ep_localcontrollers + '/' + str(lc) + '/switches/' + str(switch)

    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception as e:
        raise e
    return r


def get_localcontroller_switch_ports(headers,
                                     url_sdx_cont,
                                     lc, 
                                     switch):
    url = url_sdx_cont + ep_localcontrollers + '/' + str(lc) + '/switches/' + str(switch) + '/ports'

    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception as e:
        raise e
    return r



def get_localcontroller_switch_port(headers,
                                    url_sdx_cont,
                                    lc,
                                    switch,
                                    port):
    url = url_sdx_cont + ep_localcontrollers + '/' + str(lc) + '/switches/' + str(switch) + '/ports/' + str(port)

    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception as e:
        raise e
    return r


def get_users(headers,
              url_sdx_cont):
    url = url_sdx_cont + ep_users

    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception as e:
        raise e
    return r


def get_user(headers,
             url_sdx_cont,
             user):
    url = url_sdx_cont + ep_users + '/' + str(user)

    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception as e:
        raise e
    return r



def get_user_permissions(headers,
                         url_sdx_cont,
                         user):
    url = url_sdx_cont + ep_users + '/' + str(user) + '/permissions'

    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception as e:
        raise e
    return r


def get_user_policies(headers,
                      url_sdx_cont,
                      user):
    url = url_sdx_cont + ep_users + '/' + str(user) + '/policies'

    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception as e:
        raise e
    return r


def get_policies(headers,
                url_sdx_cont):
    url = url_sdx_cont + ep_policies

    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception as e:
        raise e
    return r


def get_policy(headers,
               url_sdx_cont,
               policy_number):
    url = url_sdx_cont + ep_policies + '/number' + str(policy_number)

    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception as e:
        raise e
    return r


def delete_policy(headers,
                  url_sdx_cont,
                  policy_number):
    url = url_sdx_cont + ep_policies + '/number' + str(policy_number)

    try:
        r = requests.delete(url, headers=headers, verify=False)
    except Exception as e:
        raise e
    return r


def get_policy_type(headers,
                    url_sdx_cont):
    url = url_sdx_cont + ep_policies + '/type' 

    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception as e:
        raise e
    return r


def get_policy_type_policytype(headers,
                               url_sdx_cont,
                               policy_type):
    url = url_sdx_cont + ep_policies + '/type/' + str(policy_type)
    
    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception as e:
        raise e
    return r
    

def post_policy_type_endpoint(headers,
                              url_sdx_cont,
                              deadline,
                              srcendpoint,
                              dstendpoint,
                              dataquantity):

    url = url_sdx_cont + ep_policies + '/type/EndpointConnection'

    data = {
             'deadline':deadline,
             'srcendpoint': srcendpoint,
             'dstendpoint': dstendpoint,
             'dataquantity': dataquantity
           }

    

    try:
        r = requests.post(url ,data=data, headers=headers, verify=False)

    except Exception as e:
        raise e
    return r


def post_policy_type_l2multipoint(headers,
                                  url_sdx_cont,
                                  starttime,
                                  endtime,
                                  endpoints,
                                  bandwidth ):
    url = url_sdx_cont + ep_policies + '/type/L2Multipoint'

    data = {
             'starttime':starttime,
             'endtime': endtime,
             'endpoints': endpoints,
             'bandwidth': bandwidth
           }



    try:
        r = requests.post(url, data=data, headers=headers, verify=False)

    except Exception as e:
        raise e
    return r


def post_policy_type_l2tunnel(headers,
                              url_sdx_cont,
                              starttime,
                              endtime,   
                              endpoints,   
                              bandwidth ):
    url = url_sdx_cont + ep_policies + '/type/L2Tunnel'

    data = {
             'starttime':starttime,
             'endtime': endtime,
             'srcswitch':srcswitch,
             'dstswitch':dstswitch,
             'srcport':srcport,
             'dstport':dstport,
             'srcvlan':srcvlan,
             'dstvlan':dstvlan,
             'bandwidth': bandwidth
           }



    try:
        r = requests.post(url, data=data, headers=headers, verify=False)

    except Exception as e:
        raise e
    return r





def post_policy_type_sdxingresgress(headers,
                                    url_sdx_cont,
                                    deadline,
                                    srcendpoint,
                                    dstendpoint,
                                    dataquantity):

    url = url_sdx_cont + ep_policies + '/type/EndpointConnection'

    data = {

             'starttime':starttime,
             'endtime': endtime,
             'switch':switch,
             'matches':matches,
             'actions':actions
           
           }

    try:
        r = requests.post(url ,data=data, headers=headers, verify=False)

    except Exception as e:
        raise e
    return r
