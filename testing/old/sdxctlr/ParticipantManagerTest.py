# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the AuthorizationInspector class

import unittest
import threading
import mock

from sdxctlr.ParticipantManager import *

CONFIG_FILE = 'test_manifests/participants.manifest'
class SingletonTest(unittest.TestCase):
    @mock.patch('sdxctlr.ParticipantManager.AuthorizationInspector',
                autospec=True)
    @mock.patch('sdxctlr.ParticipantManager.AuthenticationInspector',
                autospec=True)
    def test_singleton(self, authentication, authorization):
        firstManager = ParticipantManager(CONFIG_FILE)
        secondManager = ParticipantManager(CONFIG_FILE)

        self.failUnless(firstManager is secondManager)

class VerifyParticipantsTest(unittest.TestCase):
    @mock.patch('sdxctlr.ParticipantManager.AuthorizationInspector',
                autospec=True)
    @mock.patch('sdxctlr.ParticipantManager.AuthenticationInspector',
                autospec=True)
    def test_get_user(self, authentication, authorization):
        man = ParticipantManager(CONFIG_FILE)

        username = "sdonovan"
        credentials = "1234"
        permitted_actions = ['tbd']

        part = man._get_user(username)
        self.failUnless(part != None)
        self.failUnless(part.username == username)
        self.failUnless(part.credentials == credentials)
        self.failUnless(part.authorizations == permitted_actions)

    @mock.patch('sdxctlr.ParticipantManager.AuthorizationInspector',
                autospec=True)
    @mock.patch('sdxctlr.ParticipantManager.AuthenticationInspector',
                autospec=True)
    def test_get_bad_user(self, authentication, authorization):
        man = ParticipantManager(CONFIG_FILE)

        username = "NOTREAL"

        self.failUnless(man._get_user(username) == None)


    @mock.patch('sdxctlr.ParticipantManager.AuthorizationInspector',
                autospec=True)
    @mock.patch('sdxctlr.ParticipantManager.AuthenticationInspector',
                autospec=True)
    def test_add_user(self, authentication, authorization):
        man = ParticipantManager(CONFIG_FILE)

        username = "newuser"
        credentials = "2345"
        permitted_actions = ['tbd']

        man.add_user(username, credentials, permitted_actions)
        part = man._get_user(username)
        self.failUnless(part != None)
        self.failUnless(part.username == username)
        self.failUnless(part.credentials == credentials)
        self.failUnless(part.authorizations == permitted_actions)

        # Make sure old one's still there.
        username = "sdonovan"
        credentials = "1234"
        permitted_actions = ['tbd']

        part = man._get_user(username)
        self.failUnless(part != None)
        self.failUnless(part.username == username)
        self.failUnless(part.credentials == credentials)
        self.failUnless(part.authorizations == permitted_actions)        

        
if __name__ == '__main__':
    unittest.main()
