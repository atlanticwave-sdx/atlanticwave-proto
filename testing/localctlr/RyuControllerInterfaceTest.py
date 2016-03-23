# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import unittest
import mock
import subprocess
from localctlr.RyuControllerInterface import *
from localctlr.RyuTranslateInterface import *
from shared.OpenFlowRule import OpenFlowRule
from shared.match import *
from shared.action import *
from shared.instruction import *
from shared.offield import *
from time import sleep

class RyuControllerInterfaceInit(unittest.TestCase):

    @mock.patch('threading.Thread.start', autospec=True) # Don't want it launching the actual Ryu thread
    def atest_basic_init(self, threadpatch):
        ctlrint = RyuControllerInterface()
        

class RyuControllerInterfaceSendRecv(unittest.TestCase):

    @mock.patch('threading.Thread.start', autospec=True) # Don't want it launching the actual Ryu thread
    def atest_send_recv(self, threadpatch):
        ctlrint = RyuControllerInterface()
        rule = OpenFlowRule(["a"])
        
        ctlrint.send_command(rule)
        ctlrint.remove_rule(rule)        
        

class RyuControllerFullTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Taken and modified from  RyuTranslateInterfaceTest.py
        # Setup RyuControllerInterface, which sets up RyuTranslateInterface
        cls.ctlrint = RyuControllerInterface()
        cp = RyuCrossPollinate()
        while(cp.TranslateInterface == None):
            # Wait for cross pollination
            print "Waiting for cross pollination" 
            sleep(1)
        cls.trans = cp.TranslateInterface

        # Setup the virtual switch
        subprocess.check_call(['mn', '-c'])
        subprocess.check_call(['ovs-vsctl', 'add-br', 'br_ovs'])
        subprocess.check_call(['ovs-vsctl', 'add-port', 'br_ovs', 'vi0', '--', 'set', 'Interface', 'vi0', 'type=internal'])
        subprocess.check_call(['ovs-vsctl', 'set', 'bridge', 'br_ovs', 'other-config:datapath-id=0000000000000001'])
        subprocess.check_call(['ovs-vsctl', 'set-controller', 'br_ovs', 'tcp:127.0.0.1:6633'])


        # Wait for switch to connect to controller
        while(len(cls.trans.datapaths.keys()) == 0):
            print "Waiting " + str(cls.trans.datapaths)
            sleep(1)

        print "Datapaths: " + str(cls.trans.datapaths.keys())
        cls.datapath = cls.trans.datapaths[cls.trans.datapaths.keys()[0]]

    @classmethod
    def tearDownClass(cls):
        # Delete virtual switch
        # FIXME: whenever this is called, there is an error: "cannot switch to a different thread"
        #subprocess.check_call(['ovs-vsctl', 'del-br', 'br_ovs'])
        #sleep(5)
        print "end of tearDownClass"

    def test_rule_installation(self):
        match = OpenFlowMatch([ETH_DST("00:00:00:00:00:01")])
        actionlist = [action_SET_FIELD(ETH_DST("00:00:00:00:00:02"))]
        instruction = instruction_APPLY_ACTIONS(actionlist)
        ofr = OpenFlowRule(match, instruction)

        self.ctlrint.send_command(ofr)

        #output = subprocess.check_output(['ovs-ofctl', 'dump-flows', 'br_ovs'])
        #print output
        print "End of test_rule_installation"
        

if __name__ == '__main__':
    unittest.main()
