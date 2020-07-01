from __future__ import unicode_literals
# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the AuthorizationInspector class

import unittest
import threading
#import mock

from sdxctlr.AuthorizationInspector import *


class SingletonTest(unittest.TestCase):
    def test_singleton(self):
        firstInspector = AuthorizationInspector()
        secondInspector = AuthorizationInspector()

        self.assertTrue(firstInspector is secondInspector)


#FIXME: This is boring because the AuthorizationInspector is boring right now.
#Once the AuthorizationInspector has been fleshed out, this should be as well.

if __name__ == '__main__':
    unittest.main()
