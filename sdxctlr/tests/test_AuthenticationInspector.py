from __future__ import unicode_literals
# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the AuthenticationInspector class

import unittest
import threading
#import mock

from sdxctlr.AuthenticationInspector import *


class SingletonTest(unittest.TestCase):
    def test_singleton(self):
        firstInspector = AuthenticationInspector()
        secondInspector = AuthenticationInspector()
        self.assertTrue(firstInspector is secondInspector)

class AddingUsers(unittest.TestCase):
    def test_add_single_user(self):
        user = "john"
        credentials = "pa$$word"
        
        ai = AuthenticationInspector()
        ai.add_user(user, credentials)
        self.assertTrue(ai.is_authenticated(user, credentials))

    def test_add_many_users(self):
        user1 = "natasha"
        credentials1 = "moose"
        user2 = "boris"
        credentials2 = "squirrel"
        userlist = ((user1, credentials1),
                    (user2, credentials2))
        ai = AuthenticationInspector()
        ai.add_users(userlist)
        self.assertTrue(ai.is_authenticated(user1, credentials1))
        self.assertTrue(ai.is_authenticated(user2, credentials2))


    def test_overwrite_user(self):
        user = "bob"
        credentials1 = "qwerty"
        credentials2 = "asdf"

        ai = AuthenticationInspector()
        ai.add_user(user, credentials1)
        self.assertTrue(ai.is_authenticated(user, credentials1))

        # Change password
        ai.add_user(user, credentials2)
        self.assertTrue(ai.is_authenticated(user, credentials2))
        self.assertEqual(ai.is_authenticated(user, credentials1),
                             False)

class NonUserTest(unittest.TestCase):
    def test_non_user(self):
        user = "badname"
        credentials = "badnamepw"
        ai = AuthenticationInspector()
        self.assertEqual(ai.is_authenticated(user, credentials),
                             False)

    def test_bad_password(self):
        user = "james"
        credentials = "beard"
        badcredentials = "moustache"

        ai = AuthenticationInspector()
        ai.add_user(user, credentials)
        self.assertTrue(ai.is_authenticated(user, credentials))
        self.assertEqual(ai.is_authenticated(user, badcredentials),
                             False)


if __name__ == '__main__':
    unittest.main()
