# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project

<<<<<<< HEAD
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
        
        
=======

# Unit tests for RyuControllerInterface class

import unittest
import mock
from time import sleep
from localctlr.RyuControllerInterface import RyuControllerInterface

>>>>>>> 6d1c828ae5f55bfc3739ecf9f07dd80ff6e082d7



if __name__ == '__main__':
    unittest.main()
