# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for LocalController class

import unittest
import mock
from localctlr.LocalController import *

class InitController(unittest.TestCase):
#    @mock.patch('localctlr.LocalController.shared.Connection.select', autospec=True)
#    @mock.patch('shared.Connection.select', autospec=True)
    @mock.patch('localctlr.LocalController.SDXControllerConnectionManager', autospec=True)
    @mock.patch('localctlr.LocalController.RyuControllerInterface', autospec=True)
    def test_basic_init(self, ryuctlr, sdxcxn):
        ctlr = LocalController()

    @mock.patch('localctlr.SDXControllerConnectionManager.SDXControllerConnectionManager')
    @mock.patch('localctlr.RyuControllerInterface.RyuControllerInterface')
    def test_singleton(self, ryuctlr, sdxcxn):
        first_ctlr = LocalController()
        second_ctlr = LocalController()

        self.failUnless(first_ctlr is second_ctlr)


class StartController(unittest.TestCase):
    @mock.patch('shared.Connection.select', autospec=True)    
    @mock.patch('localctlr.LocalController.SDXControllerConnectionManager', autospec=True)
    @mock.patch('localctlr.LocalController.RyuControllerInterface', autospec=True)
    def test_start(self, ryuctlr, sdxcxn, selectmock):
        ctlr = LocalController()
        ctlr.start()







if __name__ == '__main__':
    unittest.main()
