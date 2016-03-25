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

        # Setup the virtual switch
        subprocess.check_call(['mn', '-c'])
        subprocess.call(['fuser', '-k', '55767/tcp'])
        subprocess.call(['fuser', '-k', '55767/tcp'])
        subprocess.check_call(['ovs-vsctl', 'add-br', 'br_ovs'])
        subprocess.check_call(['ovs-vsctl', 'add-port', 'br_ovs', 'vi0', '--', 'set', 'Interface', 'vi0', 'type=internal'])
        subprocess.check_call(['ovs-vsctl', 'set', 'bridge', 'br_ovs', 'other-config:datapath-id=0000000000000001'])
        subprocess.check_call(['ovs-vsctl', 'set-controller', 'br_ovs', 'tcp:127.0.0.1:6633'])


        # Setup RyuControllerInterface, which sets up RyuTranslateInterface
        # Only returns once RyuTranslateInterface has a datapath.
        cls.ctlrint = RyuControllerInterface()

    @classmethod
    def tearDownClass(cls):
        # Delete virtual switch
        # FIXME: whenever this is called, there is an error: "cannot switch to a different thread"
        #subprocess.check_call(['ovs-vsctl', 'del-br', 'br_ovs'])
        #sleep(5)
        cls.ctlrint.inter_cm_cxn.close()
        cls.ctlrint.inter_cm.close_listening_port()
        subprocess.call(['fuser', '-k', '55767/tcp'])

    def test_rule_installation(self):
        match = OpenFlowMatch([ETH_DST("00:00:00:00:00:01")])
        actionlist = [action_SET_FIELD(ETH_DST("00:00:00:00:00:02"))]
        instruction = instruction_APPLY_ACTIONS(actionlist)
        ofr = OpenFlowRule(match, instruction)

        self.ctlrint.send_command(ofr)

        output = subprocess.check_output(['ovs-ofctl', 'dump-flows', 'br_ovs'])
        lines = output.split('\n')
        
        # "cookie=0x0, duration=0.005s, table=0, n_packets=0, n_bytes=0, idle_age=0, priority=100,dl_dst=00:00:00:00:00:01 actions=mod_dl_dst:00:00:00:00:00:02"
        self.failUnlessEqual(lines[1].split(',')[6].strip(),
                             "priority=100")
        self.failUnlessEqual(lines[1].split(',')[7].strip(), 
                             "dl_dst=00:00:00:00:00:01 actions=mod_dl_dst:00:00:00:00:00:02")

    def test_rule_removal(self):
        match = OpenFlowMatch([ETH_DST("00:00:00:00:00:01")])
        actionlist = [action_SET_FIELD(ETH_DST("00:00:00:00:00:02"))]
        instruction = instruction_APPLY_ACTIONS(actionlist)
        ofr = OpenFlowRule(match, instruction)

        self.ctlrint.remove_rule(ofr)

        output = subprocess.check_output(['ovs-ofctl', 'dump-flows', 'br_ovs'])
        lines = output.split('\n')
        
        # ''
        self.failUnlessEqual(lines[1].strip(), "")
        
        

if __name__ == '__main__':
    unittest.main()
