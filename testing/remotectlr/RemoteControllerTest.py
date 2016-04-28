# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for LocalController class

import unittest
import mock
import subprocess
import os
import json
from localctlr.LocalController import *
from remotectlr.config_parser_ctlr import ConfigParserCtlr
from time import sleep

FNULL = open(os.devnull, 'w')

class RemoteControllerTest(unittest.TestCase):
    
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

        # Parse test file
        with open("rctest.json") as data_file:
            data = json.load(data_file)
        cls.tests = data['tests']


        # Start the Local Controller
        cls.lc = subprocess.Popen(["python", "LocalControllerHarness.py"], stdout=subprocess.PIPE)
        
        # Set up the Remote Controller
        cls.rc = ConfigParserCtlr()

        print "Everything is up, waiting on connections."
        while cls.rc.is_connected() == False:
            print "Waiting for harness connection"
            sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.rc.close_cxn()
        cls.lc.kill()
        

    def call_test_rule_installation(self, num, test6, test7, test8=None, test9=None, test10=None):
        # Based on LocalControllerTest
        #print "test_rule_installation_" + str(num)
        self.rc.run_configuration()      # Configuration needs to be populated first
        sleep(0.01)                      # To make sure the rule changes have propogated.
        output = subprocess.check_output(['ovs-ofctl', 'dump-flows', 'br_ovs'])
        lines = output.split('\n')

        print lines


        self.rc.run_configuration(SDX_RM_RULE)
        sleep(0.01) # To make sure the rule changes have propogated.
        output = subprocess.check_output(['ovs-ofctl', 'dump-flows', 'br_ovs'])
        rmlines = output.split('\n')
        pass

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

    def run_test(self, testnum):
        test = self.tests[testnum]

        self.rc.parse_configuration(test['conf_file'])
        self.call_test_rule_installation(**test['results'])

    def test_with_local_ctlr_0(self):
        self.run_test(0)

    def test_with_local_ctlr_1(self):
        self.run_test(1)


# I think I'll need test file pairs: one that's the JSON test file, one that's the strings for testing. 
# looking at LocalControllerTest as the basis for what I'm working on.




if __name__ == '__main__':
    unittest.main()
