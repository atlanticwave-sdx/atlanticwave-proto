# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for LocalController class

import unittest
import mock
import subprocess
from localctlr.LocalController import *
from time import sleep

class LocalControllerTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Taken and modified from  RyuControllerInterfaceTest.py

        # Setup the virtual switch
        subprocess.check_call(['mn', '-c'])
        subprocess.call(['fuser', '-k', '55767/tcp'])
        subprocess.call(['fuser', '-k', '55767/tcp'])
        subprocess.call(['fuser', '-k', '5555/tcp'])
        subprocess.call(['fuser', '-k', '5555/tcp'])
        subprocess.check_call(['ovs-vsctl', 'add-br', 'br_ovs'])
        subprocess.check_call(['ovs-vsctl', 'add-port', 'br_ovs', 'vi0', '--', 'set', 'Interface', 'vi0', 'type=internal'])
        subprocess.check_call(['ovs-vsctl', 'set', 'bridge', 'br_ovs', 'other-config:datapath-id=0000000000000001'])
        subprocess.check_call(['ovs-vsctl', 'set-controller', 'br_ovs', 'tcp:127.0.0.1:6633'])


        # Setup RyuControllerInterface, which sets up RyuTranslateInterface
        # Only returns once RyuTranslateInterface has a datapath.
        cls.harness = RemoteControllerHarness()
        cls.ctlrint = RyuControllerInterface()
        while cls.harness.is_connected() == False:
            print "Waiting for harness connection"
            sleep(1)

        cls.ctlrint.start_main_loop()

    @classmethod
    def tearDownClass(cls):
        # Delete virtual switch
        # FIXME: whenever this is called, there is an error: "cannot switch to a different thread"
        #subprocess.check_call(['ovs-vsctl', 'del-br', 'br_ovs'])
        #sleep(5)
        cls.ctlrint.inter_cm_cxn.close()
        cls.ctlrint.inter_cm.close_listening_port()
        subprocess.call(['fuser', '-k', '55767/tcp'])
        subprocess.call(['fuser', '-k', '5555/tcp'])

    def call_test_rule_installation(self, num):
        rule = self.harness.examples[num]
        self.harness.send_new_command(rule)
        output = subprocess.check_output(['ovs-ofctl', 'dump-flows', 'br_ovs'])
        
        self.harness.send_rm_command(rule)
        output = subprocess.check_output(['ovs-ofctl', 'dump-flows', 'br_ovs'])

    def test_rule_installation_0(self):
        self.call_test_rule_installation(0)
    def test_rule_installation_1(self):
        self.call_test_rule_installation(1)
    def test_rule_installation_2(self):
        self.call_test_rule_installation(2)
    def test_rule_installation_3(self):
        self.call_test_rule_installation(3)




if __name__ == '__main__':
    unittest.main()
