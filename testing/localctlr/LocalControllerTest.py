# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for LocalController class

import unittest
import mock
import subprocess
import os
from localctlr.LocalController import *
from RemoteControllerHarness import RemoteControllerHarness
from time import sleep

FNULL = open(os.devnull, 'w')

class LocalControllerTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Taken and modified from  RyuControllerInterfaceTest.py

        # Setup the virtual switch
        print "Set up virtual switch"
        subprocess.check_call(['mn', '-c'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(['fuser', '-k', '55767/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(['fuser', '-k', '55767/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(['fuser', '-k', '5555/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(['fuser', '-k', '5555/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.check_call(['ovs-vsctl', 'add-br', 'br_ovs'])
        subprocess.check_call(['ovs-vsctl', 'add-port', 'br_ovs', 'vi0', '--', 'set', 'Interface', 'vi0', 'type=internal'])
        subprocess.check_call(['ovs-vsctl', 'set', 'bridge', 'br_ovs', 'other-config:datapath-id=0000000000000001'])
        subprocess.check_call(['ovs-vsctl', 'set-controller', 'br_ovs', 'tcp:127.0.0.1:6633'])
        print "Virtual switch is setup\n"


        # Setup RyuControllerInterface, which sets up RyuTranslateInterface
        # Only returns once RyuTranslateInterface has a datapath.
        cls.harness = RemoteControllerHarness()
        cls.ctlrint = LocalController()

#        cls.ctlrint.start_sdx_controller_connection()
        while cls.harness.is_connected() == False:
            print "Waiting for harness connection"
            sleep(1)

#        cls.ctlrint.start_main_loop()

    @classmethod
    def tearDownClass(cls):
        # Delete virtual switch
        # FIXME: whenever this is called, there is an error: "cannot switch to a different thread"
        #subprocess.check_call(['ovs-vsctl', 'del-br', 'br_ovs'])
        #sleep(5)

#        subprocess.call(['fuser', '-k', '55767/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
#        subprocess.call(['fuser', '-k', '5555/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
#        subprocess.call(['fuser', '-k', '55767/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
#        subprocess.call(['fuser', '-k', '5555/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        pass

    def call_test_rule_installation(self, num, test6, test7, test8=None, test9=None, test10=None):
        #print "test_rule_installation_" + str(num)
        print "LC: %s" % (self.ctlrint)
        self.harness.send_new_command(self.harness.examples[num])
        sleep(0.01) # To make sure the rule changes have propogated.
        output = subprocess.check_output(['ovs-ofctl', 'dump-flows', 'br_ovs'])
        lines = output.split('\n')

        self.harness.send_rm_command(self.harness.examples[num])
        sleep(0.01) # To make sure the rule changes have propogated.
        output = subprocess.check_output(['ovs-ofctl', 'dump-flows', 'br_ovs'])
        rmlines = output.split('\n')

        # Installation tests
        self.failUnlessEqual(lines[1].split(',')[6].strip(), test6)
        self.failUnlessEqual(lines[1].split(',')[7].strip(), test7)
        if test8 != None:
            self.failUnlessEqual(lines[1].split(',')[8].strip(), test8)
            
        if test9 != None:
            self.failUnlessEqual(lines[1].split(',')[9].strip(), test9)
            
        if test10 != None:
            self.failUnlessEqual(lines[1].split(',')[10].strip(), test10)

        # Removal
        self.failUnlessEqual(rmlines[1].strip(), "")

    def test_rule_installation_0(self):
        self.call_test_rule_installation(0, 
                                         "priority=100",
                                         "dl_dst=00:00:00:00:00:01 actions=mod_dl_dst:00:00:00:00:00:02")
    def test_rule_installation_1(self):
        self.call_test_rule_installation(1, 
                                         "priority=100",
                                         "ip",
                                         "nw_src=1.2.3.4 actions=mod_nw_dst:2.3.4.5")
    def test_rule_installation_2(self):
        self.call_test_rule_installation(2,
                                         "priority=100",
                                         "ip",
                                         "dl_dst=00:00:00:00:00:03",
                                         "nw_src=3.4.5.6 actions=mod_dl_src:00:00:00:00:00:04")
    def test_rule_installation_3(self):
        self.call_test_rule_installation(3, 
                                         "priority=100",
                                         "ip",
                                         "dl_dst=00:00:00:00:00:05",
                                         "nw_src=4.5.6.7 actions=mod_dl_src:00:00:00:00:00:04")

    def test_rule_installation_4(self):
        self.call_test_rule_installation(4,
                                         "priority=123",
                                         "tcp actions=output:1")
                                         




if __name__ == '__main__':
    unittest.main()
