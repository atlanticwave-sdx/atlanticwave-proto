# Copyright 2019 - Sean Donovan
# AtlanticWave/SDX Project


# Unittests for localctlr/ControllerInterface class

import unittest
from localctlr.ControllerInterface import *

class BasicTests(unittest.TestCase):
    def test_init(self):
        ctlr = ControllerInterface("test")
        
    def test_send_command(self):
        ctlr = ControllerInterface("test")
        self.failUnlessRaises(NotImplementedError, ctlr.send_command,
                              'test', 'test')

    def test_remove_rule(self):
        ctlr = ControllerInterface("test")
        self.failUnlessRaises(NotImplementedError, ctlr.remove_rule,
                              'test', 'test')
        


        
if __name__ == '__main__':
    unittest.main()
