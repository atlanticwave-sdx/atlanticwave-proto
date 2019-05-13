# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import unittest
import mock
import subprocess
from localctlr.RyuControllerInterface import *
from localctlr.RyuTranslateInterface import *
from shared.MatchActionLCRule import *
from shared.LCFields import *
from shared.LCAction import *
from time import sleep

class RyuControllerInterfaceInit(unittest.TestCase):

    @mock.patch('threading.Thread.start', autospec=True) # Don't want it launching the actual Ryu thread
    def atest_basic_init(self, threadpatch):
        ctlrint = RyuControllerInterface("127.0.0.1",
                                         55767,
                                         6633)
        

class RyuControllerInterfaceSendRecv(unittest.TestCase):

    @mock.patch('threading.Thread.start', autospec=True) # Don't want it launching the actual Ryu thread
    def atest_send_recv(self, threadpatch):
        ctlrint = RyuControllerInterface("127.0.0.1",
                                         55767,
                                         6633)
        rule = OpenFlowRule(["a"])
        
        ctlrint.send_command(rule)
        ctlrint.remove_rule(rule)        
        

class RyuControllerFullTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
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
        cls.ctlrint = RyuControllerInterface("127.0.0.1",
                                             55767,
                                             6633)

        cls.switch_id = 1

    @classmethod
    def tearDownClass(cls):
        cls.ctlrint.inter_cm_cxn.close()
        cls.ctlrint.inter_cm.close_listening_port()
        subprocess.call(['fuser', '-k', '55767/tcp'])

    def test_rule_installation(self):
        matches = [ETH_DST("00:00:00:00:00:01")]
        actions = [SetField(ETH_DST("00:00:00:00:00:02"))]
        rule = MatchActionLCRule(self.switch_id, matches, actions)
        rule.set_cookie("1234")

        self.ctlrint.send_command(self.switch_id, rule)
        sleep(1)
        output = subprocess.check_output(['ovs-ofctl', 'dump-flows', 'br_ovs'])
        #print "Installation: %s" % output
        lines = output.split('\n')
        
        # "cookie=0x0, duration=0.005s, table=0, n_packets=0, n_bytes=0, idle_age=0, priority=100,dl_dst=00:00:00:00:00:01 actions=mod_dl_dst:00:00:00:00:00:02"
        self.failUnlessEqual(lines[1].split(',')[6].strip(),
                             "priority=100")
        self.failUnlessEqual(lines[1].split(',')[7].strip(), 
                             "dl_dst=00:00:00:00:00:01 actions=mod_dl_dst:00:00:00:00:00:02")

    def test_rule_removal(self):
        cookie = "1234"
        self.ctlrint.remove_rule(self.switch_id, cookie)

        sleep(0.25)
        output = subprocess.check_output(['ovs-ofctl', 'dump-flows', 'br_ovs'])
        #print "Removal: %s" % output
        lines = output.split('\n')
        
        # ''
        self.failUnlessEqual(lines[1].strip(), "")
        
        

if __name__ == '__main__':
    unittest.main()
