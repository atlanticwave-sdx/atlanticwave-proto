from __future__ import unicode_literals
# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the AuthorizationInspector class

import unittest
import threading
import mock

from sdxctlr.LocalControllerManager import *

CONFIG_FILE = 'tests/test_manifests/lcmanagertest.manifest'
class SingletonTest(unittest.TestCase):
    @mock.patch('sdxctlr.LocalControllerManager.AuthenticationInspector',
                autospec=True)
    def test_singleton(self, authentication):
        firstManager = LocalControllerManager(manifest=CONFIG_FILE)
        secondManager = LocalControllerManager(manifest=CONFIG_FILE)

        self.assert(firstManager is secondManager)

class VerifyLCTest(unittest.TestCase):
    
    @mock.patch('sdxctlr.LocalControllerManager.AuthenticationInspector',
                autospec=True)
    def test_get_user(self, authentication):
        man = LocalControllerManager(manifest=CONFIG_FILE)

        ctlrname = 'atl'
        credentials = "atlpw"
        lcip = "10.10.10.10"
        switchips = ['10.10.10.11']

        part = man._get_controller(ctlrname)
        self.assertNotEqual(part, None)
        self.assertEquals(part.shortname, ctlrname)
        self.assertEquals(part.credentials, credentials)
        self.assertEquals(part.lcip, lcip)
        self.assertEquals(part.switchips, switchips)
               
        ctlrname = 'mia'
        credentials = "miapw"
        lcip = "10.10.10.20"
        switchips = ['10.10.10.21']

        part = man._get_controller(ctlrname)
        self.assertNotEqual(part, None)
        self.assertEquals(part.shortname, ctlrname)
        self.assertEquals(part.credentials, credentials)
        self.assertEquals(part.lcip, lcip)
        self.assertEquals(part.switchips, switchips)

        ctlrname = 'gru'
        credentials = "grupw"
        lcip = "10.10.10.30"
        switchips = ['10.10.10.31']

        part = man._get_controller(ctlrname)
        self.assertNotEqual(part, None)
        self.assertEquals(part.shortname, ctlrname)
        self.assertEquals(part.credentials, credentials)
        self.assertEquals(part.lcip, lcip)
        self.assertEquals(part.switchips, switchips)

    @mock.patch('sdxctlr.LocalControllerManager.AuthenticationInspector',
                autospec=True)
    def test_get_bad_ctlr(self, authentication):
        man = LocalControllerManager(manifest=CONFIG_FILE)

        ctlrname = "NOTREAL"
        self.assert(man._get_controller(ctlrname) == None)

        ctlrname = "nyc"
        credentials = "nycpw"
        lcip = "10.10.10.30"
        switchips = ['10.10.10.31']

        man.add_controller(ctlrname, credentials, lcip, switchips)
        part = man._get_controller(ctlrname)
        self.assert(part != None)
        self.assert(part.shortname == ctlrname)
        self.assert(part.credentials == credentials)
        self.assert(part.lcip == lcip)
        self.assert(part.switchips == switchips)

        # Make sure the old ones are still there.
        ctlrname = 'atl'
        credentials = "atlpw"
        lcip = "10.10.10.10"
        switchips = ['10.10.10.11']

        part = man._get_controller(ctlrname)
        self.assertNotEqual(part, None)
        self.assertEquals(part.shortname, ctlrname)
        self.assertEquals(part.credentials, credentials)
        self.assertEquals(part.lcip, lcip)
        self.assertEquals(part.switchips, switchips)
               
        ctlrname = 'mia'
        credentials = "miapw"
        lcip = "10.10.10.20"
        switchips = ['10.10.10.21']

        part = man._get_controller(ctlrname)
        self.assertNotEqual(part, None)
        self.assertEquals(part.shortname, ctlrname)
        self.assertEquals(part.credentials, credentials)
        self.assertEquals(part.lcip, lcip)
        self.assertEquals(part.switchips, switchips)

        ctlrname = 'gru'
        credentials = "grupw"
        lcip = "10.10.10.30"
        switchips = ['10.10.10.31']

        part = man._get_controller(ctlrname)
        self.assertNotEqual(part, None)
        self.assertEquals(part.shortname, ctlrname)
        self.assertEquals(part.credentials, credentials)
        self.assertEquals(part.lcip, lcip)
        self.assertEquals(part.switchips, switchips)

    @mock.patch('sdxctlr.LocalControllerManager.AuthenticationInspector',
                autospec=True)
    def test_add_ctlr(self, authentication):
        man = LocalControllerManager(manifest=CONFIG_FILE)


        
if __name__ == '__main__':
    unittest.main()
