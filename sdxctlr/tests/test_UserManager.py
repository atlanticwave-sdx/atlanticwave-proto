from __future__ import unicode_literals
# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the shared.UserManager class
# Based on the old ParticipantManager class tests.

import unittest
import threading
import mock

from sdxctlr.UserManager import *

db = ":memory:"
CONFIG_FILE = 'tests/test_manifests/participants.manifest'
class SingletonTest(unittest.TestCase):
    @mock.patch('sdxctlr.UserManager.AuthorizationInspector',
                autospec=True)
    @mock.patch('sdxctlr.UserManager.AuthenticationInspector',
                autospec=True)
    def test_singleton(self, authentication, authorization):
        firstManager = UserManager(db, CONFIG_FILE)
        secondManager = UserManager(db, CONFIG_FILE)

        self.assertTrue(firstManager is secondManager)

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
        self.assertTrue(part != None)
        self.assertTrue(part['username'] == username)
        self.assertTrue(part['credentials'] == credentials)
        self.assertTrue(part['permitted_actions'] == permitted_actions)

    @mock.patch('sdxctlr.UserManager.AuthorizationInspector',
                autospec=True)
    @mock.patch('sdxctlr.UserManager.AuthenticationInspector',
                autospec=True)
    def test_get_bad_user(self, authentication, authorization):
        man = UserManager(db, CONFIG_FILE)

        username = "NOTREAL"

        self.assertEqual(man.get_user(username), None)


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
        self.assertNotEqual(None, part)
        self.assertEqual(username, part['username'])
        self.assertEqual(credentials, part['credentials'])
        self.assertEqual(organization, part['organization'])
        self.assertEqual(contact, part['contact'])
        self.assertEqual(typeval, part['type'])
        self.assertEqual(permitted_actions, part['permitted_actions'])
        self.assertEqual(restrictions, part['restrictions'])

        # Make sure old one's still there.
        username = "sdonovan"
        credentials = "1234"
        permitted_actions = ['tbd']

        part = man.get_user(username)
        self.assertNotEqual(part, None)
        self.assertEqual(part['username'], username)
        self.assertEqual(part['credentials'], credentials)
        self.assertEqual(part['permitted_actions'], permitted_actions)

        
if __name__ == '__main__':
    unittest.main()
