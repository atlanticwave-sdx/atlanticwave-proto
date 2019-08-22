# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import unittest
import mock
import subprocess
import os
from localctlr.RyuControllerInterface import *
from localctlr.RyuTranslateInterface import *
from shared.MatchActionLCRule import *
from shared.LCFields import *
from shared.LCAction import *
from lib.Connection import Connection
from time import sleep

FNULL = open(os.devnull, 'w')

NAME = "atl"
MANIFEST = os.getcwd() + '/rtitest.manifest'
IP = "127.0.0.1"
RYUCXNPORT = 55767
OFPORT = 6633
switch_id = 1


def lccallback(a,b):
    print "LCCALLBACK: %s, %s"% (a,b)

class RyuControllerInterfaceInit(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        subprocess.call(['pkill', 'ryu-manager'])

    def test_basic_init(self):
        ctlrint = RyuControllerInterface(NAME, MANIFEST, IP, 
                                         RYUCXNPORT, OFPORT,
                                         lccallback,
                                         run_ryu_manager=False,
                                         run_main_loop=False)
        

class RyuControllerInterfaceSendRecv(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        subprocess.call(['pkill', 'ryu-manager'])


    def test_send_recv(self):
        ctlrint = RyuControllerInterface(NAME, MANIFEST, IP, 
                                         RYUCXNPORT, OFPORT,
                                         lccallback,
                                         run_ryu_manager=False,
                                         run_main_loop=False)

        #ctlrint.inter_cm_cxn = cxnpatch(None, None, None) 
        rule = MatchActionLCRule(switch_id,
                                 [IP_PROTO(6), ETH_TYPE(0x0800)],
                                 [Forward(1)])
        cookie = 100
        rule.set_cookie(cookie)
        
        #ctlrint.send_command(switch_id,rule)
        #cxnpatch.send_cmd.assert_called()
        #cxnpatch.send_cmd.assert_called_with(ICX_ADD, (switch_id, rule))
        #ctlrint.remove_rule(switch_id,cookie)        
        #cxnpatch.send_cmd.assert_called()
        #cxnpatch.send_cmd.assert_called_with(ICX_REMOVE, (switch_id, cookie))
        

class RyuControllerFullTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Setup the virtual switch
        #subprocess.check_call(['mn', '-c'])
        #subprocess.call(['fuser', '-k', '55767/tcp'])
        #subprocess.call(['fuser', '-k', '55767/tcp'])
        subprocess.check_call(['ovs-vsctl', 'add-br', 'br_ovs'])
        subprocess.check_call(['ovs-vsctl', 'add-port', 'br_ovs', 'vi0', '--', 'set', 'Interface', 'vi0', 'type=internal'])
        subprocess.check_call(['ovs-vsctl', 'set', 'bridge', 'br_ovs', 'protocols=OpenFlow13'])
        subprocess.check_call(['ovs-vsctl', 'set', 'bridge', 'br_ovs', 'other-config:datapath-id=0000000000000001'])
        subprocess.check_call(['ovs-vsctl', 'set-controller', 'br_ovs', 'tcp:127.0.0.1:6633'])


        # Setup RyuControllerInterface, which sets up RyuTranslateInterface
        # Only returns once RyuTranslateInterface has a datapath.
        cls.ctlrint = RyuControllerInterface(NAME, MANIFEST, IP, 
                                             RYUCXNPORT, OFPORT,
                                             lccallback)

        cls.switch_id = 1

    @classmethod
    def tearDownClass(cls):
        subprocess.call(['pkill', 'ryu-manager'])
        cls.ctlrint.inter_cm_cxn.close()
        cls.ctlrint.inter_cm.close_listening_port()
        
        subprocess.check_call(['ovs-vsctl', 'del-port', 'vi0'])
        subprocess.check_call(['ovs-vsctl', 'del-br', 'br_ovs'])
        sleep(5)
        
        #subprocess.check_call(['mn', '-c'])
        #subprocess.call(['fuser', '-k', '55767/tcp'])
        #subprocess.call(['fuser', '-k', '55767/tcp'])
        #subprocess.call(['fuser', '-k', '6633/tcp'])
        #subprocess.call(['fuser', '-k', '6633/tcp'])
        sleep(1)

    def call_test_rule_installation(self, rule, test5, test6, test7=None, 
                                    test8=None, test9=None, test10=None):
        sleep(1)
        #print "test_rule_installation_" + str(num)
        #print "LC: %s" % (self.ctlrint)
        print "SENDING NEW COMMAND: %s" % rule
        self.ctlrint.send_command(self.switch_id, rule)
        sleep(1) # To make sure the rule changes have propogated.
                 # 0.1 second isn't enough
        output = subprocess.check_output(['ovs-ofctl', '-O', 'OpenFlow13','dump-flows', 'br_ovs'])
        print "\nINSTALL OUTPUT: %s\n" % output
        lines = output.split('\n')

        self.ctlrint.remove_rule(self.switch_id, rule.get_cookie())
        sleep(1) # To make sure the rule changes have propogated.
        output = subprocess.check_output(['ovs-ofctl', '-O', 'OpenFlow13','dump-flows', 'br_ovs'])
        print "\nREMOVE OUTPUT: %s\n" % output
        rmlines = output.split('\n')

        # Installation tests
        for line in lines:
            #int "CHECKING LINE: %s" % line
            if "priority=100" not in line:
                continue
            print "MATCHED LINE:\n     %s" % line
            count = 0
            for e in line.split(','):
                print "%d:%s" % (count, e)
                count += 1
            self.failUnlessEqual(line.split(',')[5].strip(), test5)
            self.failUnlessEqual(line.split(',')[6].strip(), test6)
            if test7 != None:
                self.failUnlessEqual(line.split(',')[7].strip(), test7)
            if test8 != None:
                self.failUnlessEqual(line.split(',')[8].strip(), test8)
            if test9 != None:
                self.failUnlessEqual(line.split(',')[9].strip(), test9)
            if test10 != None:
                self.failUnlessEqual(line.split(',')[10].strip(), test10)

        # Removal
        for line in rmlines:
            self.failUnless("priority=100" not in line)

    def test_rule_installation(self):
        matches = [ETH_DST("00:00:00:00:00:01")]
        actions = [SetField(ETH_DST("00:00:00:00:00:02"))]
        rule = MatchActionLCRule(self.switch_id, matches, actions)
        rule.set_cookie("1234")

        self.call_test_rule_installation(rule,
                                         "priority=100",
                                         "dl_dst=00:00:00:00:00:01 actions=set_field:00:00:00:00:00:02->eth_dst")
        
        

if __name__ == '__main__':
    unittest.main()
