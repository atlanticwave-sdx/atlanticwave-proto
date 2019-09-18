# Copyright 2019 - Sean Donovan
# AtlanticWave/SDX Project


# Unit Tests for the RestAPI class
# Reference - https://docs.google.com/document/d/1yCbCZYFwVfDbKzIxoKz9zuhJitZVomA2aWUtsgsP7rw/edit?usp=sharing

import unittest
import threading
import subprocess
import os
import json
import re

from sdxctlr.RestAPI import *
from sdxctlr.SDXController import SDXController
from sdxctlr.TopologyManager import TopologyManager
from sdxctlr.PolicyManager import PolicyManager


DB_FILE = ":memory:"
TOPO_CONFIG_FILE = 'sdxctlr/tests/test_manifests/topo.manifest'
BASIC_MANIFEST_FILE = 'sdxctlr/tests/test_manifests/participants.manifest'
ENDPOINT_PREFIX = "http://127.0.0.1:5000"

#https://www.blog.pythonlibrary.org/2014/02/14/python-101-how-to-change-a-dict-into-a-class/
class Dict2Obj(object):
    """
    Turns a dictionary into a class
    """
 
    #----------------------------------------------------------------------
    def __init__(self, dictionary):
        """Constructor"""
        for key in dictionary:
            setattr(self, key, dictionary[key])

no_loop_options = Dict2Obj({'manifest':TOPO_CONFIG_FILE,
                            'database':DB_FILE,
                            'topo':False,
                            'host':'0.0.0.0',
                            'lcport':5555,
                            'sport':5001,
                            'port':5000,
                            'shib':False})

def add_policy(param):
    # For Policy Manager
    print "Add Policy %s" % param

def rm_policy(param):
    # For Policy Manager
    print "Rm  Policy %s" % param

class SingletonTest(unittest.TestCase):
    def test_singleton(self):
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        pm = PolicyManager(DB_FILE,
                           send_user_policy_breakdown_add=add_policy,
                           send_user_policy_breakdown_remove=rm_policy)
        first = RestAPI()
        second = RestAPI()

        self.failUnless(first is second)


# Login and Logout tests are unique in that they don't inherit from
# EndpointTestCase. This is because EndpointTestCase assumes Login/Logout works.
class EP_LOGIN_Test(unittest.TestCase):
    def setUp(self):
        self.sdx = SDXController(False, no_loop_options)
        self.cookie_file = "testing.cookie"
        self.endpoint = ENDPOINT_PREFIX + EP_LOGIN

    def tearDown(self):
        # Delete cookie
        if os.path.exists(self.cookie_file):
            os.remove(self.cookie_file)
        self.sdx = None

    def test_GET(self):
        # Make sure we can get the login form w/o logging in - No cookie.
        output = subprocess.check_call(['curl', '-X', 'GET',
                                        self.endpoint])

    def test_POST(self):
        # Make sure we can get actaully login.
        output = subprocess.check_call(['curl', '-X', 'POST',
                                        '-F', "username=sdonovan",
                                        '-F', "password=1234",
                                        self.endpoint,
                                        '-c', self.cookie_file])

        
        # Confirm that cookie exists - proof of login.
        self.failUnless(os.path.exists(self.cookie_file))

    def test_POST_failure(self):
        # Cleanup, if needed, normally taken care of by tearDown().
        if os.path.exists(self.cookie_file):
            os.remove(self.cookie_file)
        # This should fail!
        output = subprocess.check_output(['curl', '-X', 'POST',
                                          '-F', "username=sdonovan", # good user
                                          '-F', "password=4321",     # bad pw
                                          self.endpoint,
                                          '-c', self.cookie_file])
        self.failIf(os.path.exists(self.cookie_file))
        expected_output = { u"error": u"User Not Authenticated"}
        self.assertEqual(expected_output,
                         json.loads(output))

class EP_LOGOUT_Test(unittest.TestCase):
    def setUp(self):
        # Get cookie
        self.sdx = SDXController(False, no_loop_options)
        self.cookie_file = "testing.cookie"
        self.endpoint = ENDPOINT_PREFIX + EP_LOGOUT

        login_endpoint = ENDPOINT_PREFIX + EP_LOGIN

        output = subprocess.check_call(['curl', '-X', 'POST',
                                        '-F', "username=sdonovan",
                                        '-F', "password=1234",
                                        login_endpoint,
                                        '-c', self.cookie_file])

        
        # Confirm that cookie exists - proof of login.
        self.failUnless(os.path.exists(self.cookie_file))

    def tearDown(self):
        # Delete cookie
        if os.path.exists(self.cookie_file):
            os.remove(self.cookie_file)
        self.sdx = None

    def test_GET_no_login(self):
        # Make sure we can get the logout form w/o logging in - No cookie.
        output = subprocess.check_call(['curl', '-X', 'GET',
                                        self.endpoint])

    def test_GET_with_login(self):
        # Make sure we can get the logout form with login
        output = subprocess.check_call(['curl', '-X', 'GET',
                                        self.endpoint,
                                        '-c', self.cookie_file])

    def test_POST(self):
        # Make sure we can get actaully logout
        output = subprocess.check_call(['curl', '-X', 'POST',
                                        self.endpoint,
                                        '-c', self.cookie_file])

class EndpointTestCase(unittest.TestCase):
    # Test framework - Parent class for endpoint tests below.
    def setUp(self):
        # Get cookie/login
        self.sdx = SDXController(False, no_loop_options)
        self.cookie_file = "testing.cookie"

        login_endpoint = ENDPOINT_PREFIX + EP_LOGIN

        output = subprocess.check_call(['curl', '-X', 'POST',
                                        '-F', "username=sdonovan",
                                        '-F', "password=1234",
                                        login_endpoint,
                                        '-c', self.cookie_file])
        # Confirm that cookie exists - proof of login.
        self.failUnless(os.path.exists(self.cookie_file))
        
        pass

    def tearDown(self):
        # Logout
        logout_endpoint = ENDPOINT_PREFIX + EP_LOGOUT
        output = subprocess.check_call(['curl', '-X', 'POST',
                                        logout_endpoint,
                                        '-c', self.cookie_file])
        
        # Delete cookie
        if os.path.exists(self.cookie_file):
            os.remove(self.cookie_file)
        self.sdx = None

    def run_case_json(self, endpoint, expected_output,
                      cookie=False, method = 'GET', data=None):
        output = None
        if data != None:
            self.assertTrue(cookie)
            print "\n\n\n##### DATA TEST - %s #####" % data
            output = subprocess.check_output(['curl', '-X', method,
                                              '-H',
                                              "Content-type: application/json",
                                              '-H', "Accept: application/json",
                                              endpoint,
                                              '-d', data,
                                              '-b', self.cookie_file])
            
        elif cookie:
            print "\n\n\n##### COOKIE TEST - %s #####" % self.cookie_file
            with open(self.cookie_file) as f:
                print(f.read())
            print "\n\n\n"
            output = subprocess.check_output(['curl', '-X', method,
                                              '-H', "Accept: application/json",
                                              endpoint,
                                              '-b', self.cookie_file])

        else:
            print "\n\n\n##### NON-COOKIE TEST #####\n\n\n"
            output = subprocess.check_output(['curl', '-X', method,
                                              '-H', "Accept: application/json",
                                              endpoint])

        print "\n\n\n"
        print endpoint   
        print output
        print "\n\n\n"
        if expected_output != "":
            self.assertEqual(expected_output,
                             json.loads(output))


# LOCAL CONTROLLER ENDPOINTS

class EP_LOCALCONTROLLER_Test(EndpointTestCase):
    def test_GET_no_login_json(self):
        endpoint = ENDPOINT_PREFIX + EP_LOCALCONTROLLER
        expected_output = {
            u"href": unicode(endpoint),
            u"links": {
                u"oneLC": {
                    u"href": unicode(endpoint + "/oneLC")
                    }
                }
            }

        self.run_case_json(endpoint, expected_output)

    def test_GET_with_login(self):
        endpoint = ENDPOINT_PREFIX + EP_LOCALCONTROLLER
        expected_output = {
            u"href": unicode(endpoint),
            u"links": {
                u"oneLC": {
                    u"href": unicode(endpoint + "/oneLC")
                    }
                }
            }

        self.run_case_json(endpoint, expected_output, True)



class EP_LOCALCONTROLLERLC_Test(EndpointTestCase):
    def test_GET_no_login_json(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "oneLC", EP_LOCALCONTROLLERLC)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = {
            u"oneLC":{
                u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC",
                u"lcip": u"127.0.0.1",
                u"operator": {
                    u"organization": u"Georgia Tech/RNOC",
                    u"administrator": u"Sean Donovan",
                    u"contact": u"sdonovan@gatech.edu"},
                u"switches": {
                    u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches",

                    u"br4": {
                        u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br4"},
                    u"br3": {
                        u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br3"},
                    u"br2": {
                        u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br2"},
                    u"br1": {
                        u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br1"}
                },
                u"internalconfig": {
                    u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/internalconfig"}
            }
        }


        self.run_case_json(endpoint, expected_output)

    def test_GET_with_login(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "oneLC", EP_LOCALCONTROLLERLC)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = {
            u"oneLC":{
                u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC",
                u"lcip": u"127.0.0.1",
                u"operator": {
                    u"organization": u"Georgia Tech/RNOC",
                    u"administrator": u"Sean Donovan",
                    u"contact": u"sdonovan@gatech.edu"},
                u"switches": {
                    u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches",

                    u"br4": {
                        u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br4"},
                    u"br3": {
                        u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br3"},
                    u"br2": {
                        u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br2"},
                    u"br1": {
                        u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br1"}
                },
                u"internalconfig": {
                    u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/internalconfig"}
            }
        }

        self.run_case_json(endpoint, expected_output, True)

    def test_GET_failure(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "FAKELC", EP_LOCALCONTROLLERLC)
        endpoint = ENDPOINT_PREFIX + suffix

        output = subprocess.check_output(['curl', '-X', 'GET',
                                          '-H', "Accept: application/json",
                                          endpoint,
                                          '-b', self.cookie_file])
        expected_output = '{}'
        self.assertEqual(expected_output, output)
        

class EP_LOCALCONTROLLERLCINT_Test(EndpointTestCase):
    def test_GET_no_login_json(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "oneLC", EP_LOCALCONTROLLERLCINT)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = { u"error": u"User Not Authenticated"}

        self.run_case_json(endpoint, expected_output)

    def test_GET_with_login(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "oneLC", EP_LOCALCONTROLLERLCINT)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = {
            u"oneLC": {
                u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/internalconfig",
                u"internalconfig": {
                    u"ryucxninternalport": 55780,
                    u"openflowport": 6680}}}

        self.run_case_json(endpoint, expected_output, True)

    def test_GET_failure(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "FAKELC", EP_LOCALCONTROLLERLCINT)
        endpoint = ENDPOINT_PREFIX + suffix

        output = subprocess.check_output(['curl', '-X', 'GET',
                                          '-H', "Accept: application/json",
                                          endpoint,
                                          '-b', self.cookie_file])
        expected_output = '{}'
        self.assertEqual(expected_output, output)
        
class EP_LOCALCONTROLLERLCSW_Test(EndpointTestCase):
    def test_GET_no_login_json(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "oneLC", EP_LOCALCONTROLLERLCSW)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = { u"error": u"User Not Authenticated"}

        self.run_case_json(endpoint, expected_output)

    def test_GET_with_login(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "oneLC", EP_LOCALCONTROLLERLCSW)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = {
            u"oneLC": {
                u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches",
                u"links": {
                    u"br1": {
                        u"href": "http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br1"},
                    u"br2": {
                        u"href": "http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br2"},
                    u"br3": {
                        u"href": "http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br3"},
                    u"br4": {"href": "http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br4"}}}}

        self.run_case_json(endpoint, expected_output, True)

    def test_GET_failure(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "FAKELC", EP_LOCALCONTROLLERLCSW)
        endpoint = ENDPOINT_PREFIX + suffix

        output = subprocess.check_output(['curl', '-X', 'GET',
                                          '-H', "Accept: application/json",
                                          endpoint,
                                          '-b', self.cookie_file])
        expected_output = '{}'
        self.assertEqual(expected_output, output)


class EP_LOCALCONTROLLERLCSWSPEC_Test(EndpointTestCase):
    def test_GET_no_login_json(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "oneLC",
                        EP_LOCALCONTROLLERLCSWSPEC, 1)
        suffix = re.sub(r'(<[a-zA-Z]*>)', "br1", suffix, 1)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = { u"error": u"User Not Authenticated"}

        self.run_case_json(endpoint, expected_output)

    def test_GET_with_login(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "oneLC",
                        EP_LOCALCONTROLLERLCSWSPEC, 1)
        suffix = re.sub(r'(<[a-zA-Z]*>)', "br1", suffix, 1)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = {
            u"br1": {
                u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br1",

                u"ip": u"127.0.0.1",
                u"brand": u"Open vSwitch",
                u"dpid": 1,
                u"friendlyname": u"br1",
                u"model": u"2.3.0",
                u"ports": {
                    u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br1/ports",
                    u"port5": {
                        u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br1/ports/5",
                        u"portnumber": 5},
                    u"port4": {
                        u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br1/ports/4",
                        u"portnumber": 4},
                    u"port2": {
                        u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br1/ports/2",
                        u"portnumber": 2},
                    u"port3": {
                        u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br1/ports/3",
                        u"portnumber": 3}}}}
        
        self.run_case_json(endpoint, expected_output, True)

    def test_GET_failure(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "FAKELC",
                        EP_LOCALCONTROLLERLCSWSPEC, 1)
        suffix = re.sub(r'(<[a-zA-Z]*>)', 'br1', suffix, 1)
        endpoint = ENDPOINT_PREFIX + suffix

        output = subprocess.check_output(['curl', '-X', 'GET',
                                          '-H', "Accept: application/json",
                                          endpoint,
                                          '-b', self.cookie_file])
        expected_output = '{}'
        self.assertEqual(expected_output, output)

class EP_LOCALCONTROLLERLCSWSPECPORT_Test(EndpointTestCase):
    def test_GET_no_login_json(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "oneLC",
                        EP_LOCALCONTROLLERLCSWSPECPORT, 1)
        suffix = re.sub(r'(<[a-zA-Z]*>)', "br1", suffix, 1)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = { u"error": u"User Not Authenticated"}

        self.run_case_json(endpoint, expected_output)

    def test_GET_with_login(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "oneLC",
                        EP_LOCALCONTROLLERLCSWSPECPORT, 1)
        suffix = re.sub(r'(<[a-zA-Z]*>)', "br1", suffix, 1)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output ={
            u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br1/ports",
            u"links": {
                u"port4": {
                    u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br1/ports/4",
                    u"portnumber": 4},
                u"port5": {
                    u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br1/ports/5",
                    u"portnumber": 5},
                u"port2": {
                    u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br1/ports/2",
                    u"portnumber": 2},
                u"port3": {
                    u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br1/ports/3",
                    u"portnumber": 3}}}
        
        self.run_case_json(endpoint, expected_output, True)

    def test_GET_failure(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "FAKELC",
                        EP_LOCALCONTROLLERLCSWSPECPORT, 1)
        suffix = re.sub(r'(<[a-zA-Z]*>)', 'br1', suffix, 1)
        endpoint = ENDPOINT_PREFIX + suffix

        output = subprocess.check_output(['curl', '-X', 'GET',
                                          '-H', "Accept: application/json",
                                          endpoint,
                                          '-b', self.cookie_file])
        expected_output = '{}'
        self.assertEqual(expected_output, output)

class EP_LOCALCONTROLLERLCSWSPECPORTSPEC_Test(EndpointTestCase):
    def test_GET_no_login_json(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "oneLC",
                        EP_LOCALCONTROLLERLCSWSPECPORTSPEC, 1)
        suffix = re.sub(r'(<[a-zA-Z]*>)', "br1", suffix, 1)
        suffix = re.sub(r'(<[a-zA-Z]*>)', "3", suffix, 1)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = { u"error": u"User Not Authenticated"}

        self.run_case_json(endpoint, expected_output)

    def test_GET_with_login(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "oneLC",
                        EP_LOCALCONTROLLERLCSWSPECPORTSPEC, 1)
        suffix = re.sub(r'(<[a-zA-Z]*>)', "br1", suffix, 1)
        suffix = re.sub(r'(<[a-zA-Z]*>)', "3", suffix, 1)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = {
            u"port3": {
                u"vlansinuse": [],
                u"bwinuse": 0,
                u"destination": u"br2",
                u"href": u"http://127.0.0.1:5000/api/v1/localcontrollers/oneLC/switches/br1/ports/3",
                u"portnumber": 3,
                u"speed": 8000000000}}
        
        self.run_case_json(endpoint, expected_output, True)

    def test_GET_failure(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "FAKELC",
                        EP_LOCALCONTROLLERLCSWSPECPORTSPEC, 1)
        suffix = re.sub(r'(<[a-zA-Z]*>)', 'br1', suffix, 1)
        suffix = re.sub(r'(<[a-zA-Z]*>)', '3', suffix, 1)
        endpoint = ENDPOINT_PREFIX + suffix

        output = subprocess.check_output(['curl', '-X', 'GET',
                                          '-H', "Accept: application/json",
                                          endpoint,
                                          '-b', self.cookie_file])
        expected_output = '{}'
        self.assertEqual(expected_output, output)


# USER ENDPOINTS
class EP_USERS_Test(EndpointTestCase):
    def test_GET_no_login_json(self):
        endpoint = ENDPOINT_PREFIX + EP_USERS
        expected_output = { u"error": u"User Not Authenticated"}

        self.run_case_json(endpoint, expected_output)

    def test_GET_with_login(self):
        endpoint = ENDPOINT_PREFIX + EP_USERS
        expected_output = {
            u"href": u"http://127.0.0.1:5000/api/v1/users",
            u"links": {
                u"sdonovan": {
                    u"href": u"http://127.0.0.1:5000/api/v1/users/sdonovan",
                    u"organization": u"Georgia Tech/RNOC",
                    u"type": u"administrator",
                    u"policies": {
                        u"href": u"http://127.0.0.1:5000/api/v1/users/sdonovan/policies"},
                    u"permissions": {
                        u"href": u"http://127.0.0.1:5000/api/v1/users/sdonovan/permissions"}},
                u"jchung": {
                    u"href": u"http://127.0.0.1:5000/api/v1/users/jchung",
                    u"organization": u"Georgia Tech/RNOC",
                    u"type": u"user",
                    u"policies": {
                        u"href": u"http://127.0.0.1:5000/api/v1/users/jchung/policies"},
                    u"permissions": {
                        u"href": u"http://127.0.0.1:5000/api/v1/users/jchung/permissions"}}}}

        self.run_case_json(endpoint, expected_output, True)
    

class EP_USERSSPEC_Test(EndpointTestCase):
    def test_GET_no_login_json(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "sdonovan",
                        EP_USERSSPEC, 1)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = { u"error": u"User Not Authenticated"}

        self.run_case_json(endpoint, expected_output)

    def test_GET_with_login(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "sdonovan",
                        EP_USERSSPEC, 1)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = {
            u"href": u"http://127.0.0.1:5000/api/v1/users/sdonovan",
            u"sdonovan": {
                u"href": u"http://127.0.0.1:5000/api/v1/users/sdonovan",
                u"organization": u"Georgia Tech/RNOC",
                u"type": u"administrator",
                u"policies": {
                    u"href": u"http://127.0.0.1:5000/api/v1/users/sdonovan/policies"},
                u"permissions": {
                    u"href": u"http://127.0.0.1:5000/api/v1/users/sdonovan/permissions"}}}
        
        self.run_case_json(endpoint, expected_output, True)

    def test_GET_failure(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "fakeuser",
                        EP_USERSSPEC, 1)
        endpoint = ENDPOINT_PREFIX + suffix

        output = subprocess.check_output(['curl', '-X', 'GET',
                                          '-H', "Accept: application/json",
                                          endpoint,
                                          '-b', self.cookie_file])
        print "output: %s\n\n\n" % output
        expected_output = '{}'
        self.assertEqual(expected_output, output)

class EP_USERSSPECPOLICIES_Test(EndpointTestCase):
    #FIXME: Should this be revisited during policies?
    def test_GET_no_login_json(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "sdonovan",
                        EP_USERSSPECPOLICIES, 1)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = { u"error": u"User Not Authenticated"}

        self.run_case_json(endpoint, expected_output)

    def test_GET_with_login(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "sdonovan",
                        EP_USERSSPECPOLICIES, 1)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = {
            u"sdonovan": {
                u"href": u"http://127.0.0.1:5000/api/v1/users/sdonovan/policies",
                u"policies": {}}}
        
        self.run_case_json(endpoint, expected_output, True)

    def test_GET_failure(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "fakeuser",
                        EP_USERSSPECPOLICIES, 1)
        endpoint = ENDPOINT_PREFIX + suffix

        output = subprocess.check_output(['curl', '-X', 'GET',
                                          '-H', "Accept: application/json",
                                          endpoint,
                                          '-b', self.cookie_file])
        print "output: %s\n\n\n" % output
        expected_output = '{}'
        self.assertEqual(expected_output, output)

class EP_USERSSPECPERMISSIONS_Test(EndpointTestCase):
    def test_GET_no_login_json(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "sdonovan",
                        EP_USERSSPECPERMISSIONS, 1)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = { u"error": u"User Not Authenticated"}

        self.run_case_json(endpoint, expected_output)

    def test_GET_with_login(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "sdonovan",
                        EP_USERSSPECPERMISSIONS, 1)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = {
            u"sdonovan": {
                u"href": u"http://127.0.0.1:5000/api/v1/users/sdonovan/permissions",
                u"permissions": [u'tbd']}}
        
        self.run_case_json(endpoint, expected_output, True)

    def test_GET_failure(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "fakeuser",
                        EP_USERSSPECPERMISSIONS, 1)
        endpoint = ENDPOINT_PREFIX + suffix

        output = subprocess.check_output(['curl', '-X', 'GET',
                                          '-H', "Accept: application/json",
                                          endpoint,
                                          '-b', self.cookie_file])
        print "output: %s\n\n\n" % output
        expected_output = '{}'
        self.assertEqual(expected_output, output)

        
# POLICIES ENDPOINTS - get only, simple preliminary tests.
class EP_POLICIES_Test(EndpointTestCase):
    def test_GET_no_login_json(self):
        endpoint = ENDPOINT_PREFIX + EP_POLICIES
        expected_output = { u"error": u"User Not Authenticated"}

        self.run_case_json(endpoint, expected_output)

    def test_GET_with_login(self):
        endpoint = ENDPOINT_PREFIX + EP_POLICIES
        expected_output = {
            u"href": u"http://127.0.0.1:5000/api/v1/policies",
            u"links": {
                u"policy2": {
                    u"href": u"http://127.0.0.1:5000/api/v1/policies/number/2",
                    u"policynumber": 2,
                    u"type": u"FloodTree",
                    u"user": u"SDXCTLR"}}}
        
        self.run_case_json(endpoint, expected_output, True)

class EP_POLICIESSPEC_Test(EndpointTestCase):
    def test_GET_no_login_json(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "2",
                        EP_POLICIESSPEC, 1)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = { u"error": u"User Not Authenticated"}

        self.run_case_json(endpoint, expected_output)

    def test_GET_with_login(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "2",
                        EP_POLICIESSPEC, 1)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = {
            u"policy2": {
                u"href": u"http://127.0.0.1:5000/api/v1/policies/number/2",
                u"policynumber": 2,
                u"json": {
                    u"FloodTree": None},
                u"type": u"FloodTree",
                u"user": u"SDXCTLR"}}
        
        self.run_case_json(endpoint, expected_output, True)

    def test_GET_failure(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "2345",
                        EP_POLICIESSPEC, 1)
        endpoint = ENDPOINT_PREFIX + suffix

        output = subprocess.check_output(['curl', '-X', 'GET',
                                          '-H', "Accept: application/json",
                                          endpoint,
                                          '-b', self.cookie_file])
        print "\n\n\nendpoint: %s\noutput: %s\n\n\n" % (endpoint, output)
        expected_output = {u"error":u"Not found"}
        self.assertEqual(expected_output,
                         json.loads(output))
        

class EP_POLICIESTYPE_Test(EndpointTestCase):
    def test_GET_no_login_json(self):
        endpoint = ENDPOINT_PREFIX + EP_POLICIESTYPE
        expected_output ={
            u"href": u"http://127.0.0.1:5000/api/v1/policies/type",
            u"LearnedDestination": {
                u"href": u"http://127.0.0.1:5000/api/v1/policies/type/LearnedDestination",
                u"type": u"LearnedDestination",
                u"example": u"http://127.0.0.1:5000/api/v1/policies/type/LearnedDestination/example.html"},
            u"FloodTree": {
                u"href": u"http://127.0.0.1:5000/api/v1/policies/type/FloodTree",
                u"type": u"FloodTree",
                u"example": u"http://127.0.0.1:5000/api/v1/policies/type/FloodTree/example.html"},
            u"L2Multipoint":{
                u"href": u"http://127.0.0.1:5000/api/v1/policies/type/L2Multipoint",
                u"type": u"L2Multipoint",
                u"example": u"http://127.0.0.1:5000/api/v1/policies/type/L2Multipoint/example.html"},
            u"EdgePort": {
                u"href": u"http://127.0.0.1:5000/api/v1/policies/type/EdgePort",
                u"type": u"EdgePort",
                u"example": u"http://127.0.0.1:5000/api/v1/policies/type/EdgePort/example.html"},
            u"L2Tunnel": {
                u"href": u"http://127.0.0.1:5000/api/v1/policies/type/L2Tunnel",
                u"type": u"L2Tunnel",
                u"example": u"http://127.0.0.1:5000/api/v1/policies/type/L2Tunnel/example.html"},
            u"EndpointConnection": {
                u"href": u"http://127.0.0.1:5000/api/v1/policies/type/EndpointConnection",
                u"type": u"EndpointConnection",
                u"example": u"http://127.0.0.1:5000/api/v1/policies/type/EndpointConnection/example.html"},
            u"SDXIngress": {
                u"href": u"http://127.0.0.1:5000/api/v1/policies/type/SDXIngress",
                u"type": u"SDXIngress",
                u"example": u"http://127.0.0.1:5000/api/v1/policies/type/SDXIngress/example.html"},
        u"SDXEgress": {
                u"href": u"http://127.0.0.1:5000/api/v1/policies/type/SDXEgress",
                u"type": u"SDXEgress",
                u"example": u"http://127.0.0.1:5000/api/v1/policies/type/SDXEgress/example.html"}}

        self.run_case_json(endpoint, expected_output)

    def test_GET_with_login(self):
        endpoint = ENDPOINT_PREFIX + EP_POLICIESTYPE
        expected_output ={
            u"href": u"http://127.0.0.1:5000/api/v1/policies/type",
            u"LearnedDestination": {
                u"href": u"http://127.0.0.1:5000/api/v1/policies/type/LearnedDestination",
                u"type": u"LearnedDestination",
                u"example": u"http://127.0.0.1:5000/api/v1/policies/type/LearnedDestination/example.html"},
            u"FloodTree": {
                u"href": u"http://127.0.0.1:5000/api/v1/policies/type/FloodTree",
                u"type": u"FloodTree",
                u"example": u"http://127.0.0.1:5000/api/v1/policies/type/FloodTree/example.html"},
            u"L2Multipoint":{
                u"href": u"http://127.0.0.1:5000/api/v1/policies/type/L2Multipoint",
                u"type": u"L2Multipoint",
                u"example": u"http://127.0.0.1:5000/api/v1/policies/type/L2Multipoint/example.html"},
            u"EdgePort": {
                u"href": u"http://127.0.0.1:5000/api/v1/policies/type/EdgePort",
                u"type": u"EdgePort",
                u"example": u"http://127.0.0.1:5000/api/v1/policies/type/EdgePort/example.html"},
            u"L2Tunnel": {
                u"href": u"http://127.0.0.1:5000/api/v1/policies/type/L2Tunnel",
                u"type": u"L2Tunnel",
                u"example": u"http://127.0.0.1:5000/api/v1/policies/type/L2Tunnel/example.html"},
            u"EndpointConnection": {
                u"href": u"http://127.0.0.1:5000/api/v1/policies/type/EndpointConnection",
                u"type": u"EndpointConnection",
                u"example": u"http://127.0.0.1:5000/api/v1/policies/type/EndpointConnection/example.html"},
            u"SDXIngress": {
                u"href": u"http://127.0.0.1:5000/api/v1/policies/type/SDXIngress",
                u"type": u"SDXIngress",
                u"example": u"http://127.0.0.1:5000/api/v1/policies/type/SDXIngress/example.html"},
        u"SDXEgress": {
                u"href": u"http://127.0.0.1:5000/api/v1/policies/type/SDXEgress",
                u"type": u"SDXEgress",
                u"example": u"http://127.0.0.1:5000/api/v1/policies/type/SDXEgress/example.html"}}
        
        self.run_case_json(endpoint, expected_output, True)

class EP_POLICIESTYPESPEC_Test(EndpointTestCase):
    def test_GET_no_login_json(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "FloodTree",
                        EP_POLICIESTYPESPEC, 1)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = { u"error": u"User Not Authenticated"}

        self.run_case_json(endpoint, expected_output)

    def test_GET_with_login(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "FloodTree",
                        EP_POLICIESTYPESPEC, 1)
        endpoint = ENDPOINT_PREFIX + suffix
        expected_output = {
            u"href": u"http://127.0.0.1:5000/api/v1/policies/type/FloodTree",
            u"policy2": {
                u"policynumber": 2,
                u"href": u"http://127.0.0.1:5000/api/v1/policies/number/2",
                u"type": u"FloodTree",
                u"user": u"SDXCTLR"}}        
        self.run_case_json(endpoint, expected_output, True)

    def test_GET_failure(self):
        suffix = re.sub(r'(<[a-zA-Z]*>)', "FAKEPolicy",
                        EP_POLICIESTYPESPEC, 1)
        endpoint = ENDPOINT_PREFIX + suffix

        output = subprocess.check_output(['curl', '-X', 'GET',
                                          '-H', "Accept: application/json",
                                          endpoint,
                                          '-b', self.cookie_file])
        print "output: %s\n\n\n" % output
        expected_output = '{}'
        self.assertEqual(expected_output, output)
# SKIPPING EP_POLICIESSPECEXAMPLE

# POLICY ENDPOINTS - with posts
class EP_POLICIESTYPESPEC_Test(EndpointTestCase):
    def test_install_and_remove(self):
        getendpoint = ENDPOINT_PREFIX + EP_POLICIES
        expected_empty_output = {
            u"href": u"http://127.0.0.1:5000/api/v1/policies",
            u"links": {
                u"policy2": {
                    u"href": u"http://127.0.0.1:5000/api/v1/policies/number/2",
                    u"policynumber": 2,
                    u"type": u"FloodTree",
                    u"user": u"SDXCTLR"}}}
        
        suffix = re.sub(r'(<[a-zA-Z]*>)', "L2Tunnel",
                        EP_POLICIESTYPESPEC, 1)
        postendpoint = ENDPOINT_PREFIX + suffix
        l2tunnel = '{"L2Tunnel":{"starttime": "1985-04-12T23:20:50","endtime": "2085-04-12T23:20:50", "srcswitch": "br1", "dstswitch": "br2", "srcport": 1, "dstport": 2, "srcvlan": 100, "dstvlan": 200, "bandwidth": 100}}'
        expected_install_output = {
            u"policy": {
                u"href": u"http://127.0.0.1:5000/api/v1/policies/number/3", 
                u"json": {
                    u"L2Tunnel": {
                        u"bandwidth": 100, 
                        u"dstport": 2, 
                        u"dstswitch": u"br2", 
                        u"dstvlan": 200, 
                        u"endtime": u"2085-04-12T23:20:50", 
                        u"srcport": 1, 
                        u"srcswitch": u"br1", 
                        u"srcvlan": 100, 
                        u"starttime": u"1985-04-12T23:20:50"
                    }
                }, 
                u"type": u"L2Tunnel", 
                u"user": u"sdonovan"
            }
        }
        
        
        expected_tunnel_output = {
            u"href": u"http://127.0.0.1:5000/api/v1/policies",
            u"links": {
                u"policy3": {
                    u"policynumber": 3,
                    u"href": u"http://127.0.0.1:5000/api/v1/policies/number/3",
                    u"type": u"L2Tunnel",
                    u"user": u"sdonovan"},
                u"policy2": {
                    u"policynumber": 2,
                    u"href": u"http://127.0.0.1:5000/api/v1/policies/number/2",
                    u"type": u"FloodTree",
                    u"user": u"SDXCTLR"}}}

        
        suffix = re.sub(r'(<[a-zA-Z]*>)', '3',
                        EP_POLICIESSPEC, 1)
        delendpoint = ENDPOINT_PREFIX + suffix
        expected_del_output = ""
        
        # make sure it's clean
        self.run_case_json(getendpoint, expected_empty_output, True)

        # install a rule
        self.run_case_json(postendpoint, expected_install_output, True,
                           'POST', l2tunnel) 

        # make sure rule got installed
        self.run_case_json(getendpoint, expected_tunnel_output, True)

        # remove rule
        self.run_case_json(delendpoint, expected_del_output, True, 'DELETE')

        # make sure rule is removed
        self.run_case_json(getendpoint, expected_empty_output, True)
        


if __name__ == '__main__':
    unittest.main()






    
