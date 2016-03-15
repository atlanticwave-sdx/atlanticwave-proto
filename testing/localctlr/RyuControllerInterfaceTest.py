# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project

import unittest
import mock
from localctlr.RyuControllerInterface import *
from shared.OpenFlowRule import OpenFlowRule


class RyuControllerInterfaceInit(unittest.TestCase):

    @mock.patch('threading.Thread.start', autospec=True) # Don't want it launching the actual Ryu thread
    def test_basic_init(self, threadpatch):
        ctlrint = RyuControllerInterface()
        

class RyuControllerInterfaceSendRecv(unittest.TestCase):

    @mock.patch('threading.Thread.start', autospec=True) # Don't want it launching the actual Ryu thread
    def test_send_recv(self, threadpatch):
        ctlrint = RyuControllerInterface()
        rule = OpenFlowRule(["a"])
        
        ctlrint.send_command(rule)
        ctlrint.remove_rule(rule)        
        
        



if __name__ == '__main__':
    unittest.main()
