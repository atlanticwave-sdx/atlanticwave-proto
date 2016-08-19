# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the AuthorizationInspector class

import unittest
import threading
import mock

from sdxctlr.LocalControllerManager import *

CONFIG_FILE = 'test_manifests/topo.manifest'
class SingletonTest(unittest.TestCase):
    @mock.patch('sdxctlr.LocalControllerManager.AuthenticationInspector',
                autospec=True)
    def test_singleton(self, authentication):
        firstManager = LocalControllerManager(CONFIG_FILE)
        secondManager = LocalControllerManager(CONFIG_FILE)

        self.failUnless(firstManager is secondManager)

class VerifyLCTest(unittest.TestCase):
    
    @mock.patch('sdxctlr.LocalControllerManager.AuthenticationInspector',
                autospec=True)
    def test_get_user(self, authentication):
        man = LocalControllerManager(CONFIG_FILE)

        ctlrname = 'atl'
        credentials = "atlpw"
        lcip = "10.10.10.10"
        switchips = ['10.10.10.11']

        part = man._get_controller(ctlrname)
        self.failUnless(part != None)
        self.failUnless(part.shortname == ctlrname)
        self.failUnless(part.credentials == credentials)
        self.failUnless(part.lcip == lcip)
        self.failUnless(part.switchips == switchips)
               
        ctlrname = 'mia'
        credentials = "miapw"
        lcip = "10.10.10.20"
        switchips = ['10.10.10.21']

        part = man._get_controller(ctlrname)
        self.failUnless(part != None)
        self.failUnless(part.shortname == ctlrname)
        self.failUnless(part.credentials == credentials)
        self.failUnless(part.lcip == lcip)
        self.failUnless(part.switchips == switchips)


    @mock.patch('sdxctlr.LocalControllerManager.AuthenticationInspector',
                autospec=True)
    def test_get_bad_ctlr(self, authentication):
        man = LocalControllerManager(CONFIG_FILE)

        ctlrname = "NOTREAL"
        self.failUnless(man._get_controller(ctlrname) == None)

        ctlrname = "nyc"
        credentials = "nycpw"
        lcip = "10.10.10.30"
        switchips = ['10.10.10.31']

        man.add_controller(ctlrname, credentials, lcip, switchips)
        part = man._get_controller(ctlrname)
        self.failUnless(part != None)
        self.failUnless(part.shortname == ctlrname)
        self.failUnless(part.credentials == credentials)
        self.failUnless(part.lcip == lcip)
        self.failUnless(part.switchips == switchips)

        # Make sure the old ones are still there.
        ctlrname = 'atl'
        credentials = "atlpw"
        lcip = "10.10.10.10"
        switchips = ['10.10.10.11']

        part = man._get_controller(ctlrname)
        self.failUnless(part != None)
        self.failUnless(part.shortname == ctlrname)
        self.failUnless(part.credentials == credentials)
        self.failUnless(part.lcip == lcip)
        self.failUnless(part.switchips == switchips)
               
        ctlrname = 'mia'
        credentials = "miapw"
        lcip = "10.10.10.20"
        switchips = ['10.10.10.21']

        part = man._get_controller(ctlrname)
        self.failUnless(part != None)
        self.failUnless(part.shortname == ctlrname)
        self.failUnless(part.credentials == credentials)
        self.failUnless(part.lcip == lcip)
        self.failUnless(part.switchips == switchips)

    @mock.patch('sdxctlr.LocalControllerManager.AuthenticationInspector',
                autospec=True)
    def test_add_ctlr(self, authentication):
        man = LocalControllerManager(CONFIG_FILE)


        
if __name__ == '__main__':
    unittest.main()
