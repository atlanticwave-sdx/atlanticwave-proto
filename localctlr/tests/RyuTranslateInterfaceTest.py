# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for RyuTranslateInterfaace

import unittest
import mock
import subprocess
import os
import re
from localctlr.RyuTranslateInterface import *
from localctlr.RyuControllerInterface import *

from shared.LCAction import *
from shared.LCFields import *
from time import sleep
from ryu.ofproto.ofproto_v1_3_parser import *

DEFAULT_SLEEP_TIME=0.1

def print_callback(msg, val):
    print "%s: %s" % (msg, val)

class RyuTranslateInit(unittest.TestCase):
    

    def atest_basic_init(self):
        translate = RyuTranslateInterface()


class RyuTranslateTests(unittest.TestCase):

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
        cls.ctlrint = RyuControllerInterface("atl", 
                                             os.getcwd() + "/rtitest.manifest",
                                             "127.0.0.1", 55767, 6633,
                                             print_callback)
        cls.switch_id = 1
        cls.cookie = "1234"

    @classmethod
    def atearDownClass(cls):
        sleep(50)
        cls.ctlrint.inter_cm_cxn.close()
        cls.ctlrint.inter_cm.close_listening_port()
        subprocess.call(['fuser', '-k', '55767/tcp'])

    ######################## TRANSLATE MATCH TESTS #########################
    def trans_match_test(self, ofm, ofpm):
        pass
        if type(ofm) != type([]):
            matches = [ofm]
        else:
            matches = ofm
        actions = [SetField(ETH_DST("00:00:00:00:00:02"))]
        rule = MatchActionLCRule(self.switch_id, matches, actions)
        rule.set_cookie(self.cookie)

        self.ctlrint.send_command(self.switch_id, rule)
        sleep(DEFAULT_SLEEP_TIME)

        output = subprocess.check_output(['ovs-ofctl', 'dump-flows', 'br_ovs'])
        match = output.split("priority=100,")[1].split(" ")[0]
#        print "Installation: %s" % output
#        print "\n    ofm:   %s" % str(ofm)
#        print "    match: %s\n" % match


        self.ctlrint.remove_rule(self.switch_id, self.cookie)
        sleep(DEFAULT_SLEEP_TIME)
        output = subprocess.check_output(['ovs-ofctl', 'dump-flows', 'br_ovs'])
#        print "Removal: %s" % output
        removalmatch = re.search("priority=100,", output)
        # ''
        self.failUnlessEqual(removalmatch, None) # Removal Failure
        self.failUnlessEqual(match, ofpm)  # Installation failure


        


    def test_trans_match_IN_PORT(self):
        self.trans_match_test(IN_PORT(1), "in_port=1")

    def test_trans_match_ETH_DST(self):
        self.trans_match_test(ETH_DST("00:00:00:00:00:01"), 
                              "dl_dst=00:00:00:00:00:01")

    def test_trans_match_ETH_SRC(self):
        self.trans_match_test(ETH_SRC("00:00:00:00:00:02"), 
                              "dl_src=00:00:00:00:00:02")

    def test_trans_match_IP_PROTO(self):
        self.trans_match_test(IP_PROTO(6), "tcp")
        self.trans_match_test(IP_PROTO(17), "udp")
        self.trans_match_test(IP_PROTO(22), "ip,nw_proto=22")

    def test_trans_match_IPV4_SRC(self):
        self.trans_match_test(IPV4_SRC("1.2.3.4"), "ip,nw_src=1.2.3.4")

    def test_trans_match_IPV4_DST(self):
        self.trans_match_test(IPV4_DST("2.3.4.5"), "ip,nw_dst=2.3.4.5")

#    def test_trans_match_IPV6_SRC(self):
#        self.trans_match_test(IPV6_SRC("2001:0db8:0000:0042:0000:8a2e:0370:7334"), 
#                        {'ipv6_src':"2001:0db8:0000:0042:0000:8a2e:0370:7334"})

#    def test_trans_match_IPV6_DST(self):
#        self.trans_match_test(IPV6_DST("2001:0db8:0000:0042:0000:8a2e:0370:7335"), 
#                        {'ipv6_dst':"2001:0db8:0000:0042:0000:8a2e:0370:7335"})

    def test_trans_match_TCP_SRC(self):
        self.trans_match_test(TCP_SRC(6), "tcp,tp_src=6")

    def test_trans_match_TCP_DST(self):
        self.trans_match_test(TCP_DST(7), "tcp,tp_dst=7")

    def test_trans_match_UDP_SRC(self):
        self.trans_match_test(UDP_SRC(8), "udp,tp_src=8")

    def test_trans_match_UDP_DST(self):
        self.trans_match_test(UDP_DST(9), "udp,tp_dst=9")

    def test_trans_match_multi(self):
         #ip not needed in the check string, as tcp implies ip
        self.trans_match_test([IPV4_SRC("4.5.6.7"), TCP_DST(3456)],
                              "tcp,nw_src=4.5.6.7,tp_dst=3456")
        self.trans_match_test([IPV4_DST("6.4.5.6"), UDP_SRC(456),IN_PORT(3)],
                              "udp,in_port=3,nw_dst=6.4.5.6,tp_src=456")




    ######################## TRANSLATE ACTION TESTS #########################

    def trans_action_test(self, ofa, ofpa):
        matches = [IPV4_DST("6.4.5.6"), UDP_SRC(456),IN_PORT(3)]
        if type(ofa) != type([]):
            actions = [ofa]
        else:
            actions = ofa
        rule = MatchActionLCRule(self.switch_id, matches, actions)
        rule.set_cookie(self.cookie)

#        print "\n\n"

        self.ctlrint.send_command(self.switch_id, rule)
        sleep(DEFAULT_SLEEP_TIME)

        output = subprocess.check_output(['ovs-ofctl', 'dump-flows', 
                                          '-O', 'OpenFlow13', 'br_ovs'])
        lines = output.split("\n")
        action = ""
        for line in lines:
            if None != re.search("priority=100,", line):
                action = line.split("actions=")[1].strip()#.split(" ")[0]
#                print "Action:    %s" %action
                break
#        print "Installation: %s" % output
#        print "\n    ofa:    %s" % str(ofa)
#        print "    action: %s" % action

        #sleep(50)


        self.ctlrint.remove_rule(self.switch_id, self.cookie)
        sleep(DEFAULT_SLEEP_TIME)
        output = subprocess.check_output(['ovs-ofctl', 'dump-flows', 
                                          '-O', 'OpenFlow13', 'br_ovs'])
#        print "Removal: %s" % output
        removalmatch = re.search("priority=100,", output)
        
        # ''
        self.failUnlessEqual(removalmatch, None) # Removal Failure
        self.failUnlessEqual(action, ofpa)  # Installation failure



    def test_trans_action_SetField(self):
        self.trans_action_test(SetField(ETH_DST("00:00:00:00:00:02")),
                               "set_field:00:00:00:00:00:02->eth_dst")
        self.trans_action_test(SetField(UDP_SRC(3456)),
                               "set_field:3456->udp_src")

        self.trans_action_test([SetField(ETH_DST("00:00:00:00:00:02")),
                                SetField(UDP_SRC(3456))],
                               "set_field:00:00:00:00:00:02->eth_dst,set_field:3456->udp_src")

    def test_trans_action_Forward(self):
        self.trans_action_test(Forward(3),
                               "output:3")
        self.trans_action_test(Forward(5),
                               "output:5")
        self.trans_action_test([Forward(5),Forward(1)],
                               "output:5,output:1")

    def test_trans_action_Continue(self):
        self.trans_action_test(Continue(),
                               "goto_table:2")

    def test_trans_action_Drop(self):
        self.trans_action_test(Drop(),
                               "clear_actions")

    def test_trans_action_SetField_and_Continue(self):
        self.trans_action_test([SetField(UDP_SRC(3456)),
                                Continue()],
                               "set_field:3456->udp_src,goto_table:2")

                               




if __name__ == '__main__':
    unittest.main()
