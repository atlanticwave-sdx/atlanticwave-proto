# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the shared.UserManager class
# Based on the old ParticipantManager class tests.

import unittest
import threading
import mock

from sdxctlr.UserManager import *

db = ":memory:"
CONFIG_FILE = 'test_manifests/participants.manifest'
class SingletonTest(unittest.TestCase):
    @mock.patch('sdxctlr.UserManager.AuthorizationInspector',
                autospec=True)
    @mock.patch('sdxctlr.UserManager.AuthenticationInspector',
                autospec=True)
    def test_singleton(self, authentication, authorization):
        firstManager = UserManager(db, CONFIG_FILE)
        secondManager = UserManager(db, CONFIG_FILE)

        self.failUnless(firstManager is secondManager)

class VerifyParticipantsTest(unittest.TestCase):
    @mock.patch('sdxctlr.UserManager.AuthorizationInspector',
                autospec=True)
    @mock.patch('sdxctlr.UserManager.AuthenticationInspector',
                autospec=True)
    def test_get_user(self, authentication, authorization):
        man = UserManager(db, CONFIG_FILE)

        username = "sdonovan"
        credentials = "1234"
        permitted_actions = ['tbd']

        part = man.get_user(username)
        self.failUnless(part != None)
        self.failUnless(part['username'] == username)
        self.failUnless(part['credentials'] == credentials)
        self.failUnless(part['permitted_actions'] == permitted_actions)

    @mock.patch('sdxctlr.UserManager.AuthorizationInspector',
                autospec=True)
    @mock.patch('sdxctlr.UserManager.AuthenticationInspector',
                autospec=True)
    def test_get_bad_user(self, authentication, authorization):
        man = UserManager(db, CONFIG_FILE)

        username = "NOTREAL"

        self.assertEquals(man.get_user(username), None)


    @mock.patch('sdxctlr.UserManager.AuthorizationInspector',
                autospec=True)
    @mock.patch('sdxctlr.UserManager.AuthenticationInspector',
                autospec=True)
    def test_add_user(self, authentication, authorization):
        man = UserManager(db, CONFIG_FILE)

        username = "newuser"
        credentials = "2345"
        permitted_actions = ['tbd']
        organization = 'cern'
        contact = 'newusers@cern.edu'
        typeval = 'administrator'
        permitted_actions = 'NOT IMPLEMENTED'
        restrictions = 'NOT IMPLEMENTED'
        user = {'username':username,
                'credentials':credentials,
                'organization':organization,
                'contact':contact,
                'type':typeval,
                'permitted_actions':permitted_actions,
                'restrictions':restrictions}
        man.add_user(user)
        part = man.get_user(username)
        self.assertNotEquals(None, part)
        self.assertEquals(username, part['username'])
        self.assertEquals(credentials, part['credentials'])
        self.assertEquals(organization, part['organization'])
        self.assertEquals(contact, part['contact'])
        self.assertEquals(typeval, part['type'])
        self.assertEquals(permitted_actions, part['permitted_actions'])
        self.assertEquals(restrictions, part['restrictions'])

        # Make sure old one's still there.
        username = "sdonovan"
        credentials = "1234"
        permitted_actions = ['tbd']

        part = man.get_user(username)
        self.assertNotEquals(part, None)
        self.assertEquals(part['username'], username)
        self.assertEquals(part['credentials'], credentials)
        self.assertEquals(part['permitted_actions'], permitted_actions)

        
if __name__ == '__main__':
    unittest.main()
