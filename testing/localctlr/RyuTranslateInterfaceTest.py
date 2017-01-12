# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for RyuTranslateInterfaace

import unittest
import mock
import subprocess
from localctlr.RyuTranslateInterface import *
from localctlr.RyuControllerInterface import *
from localctlr.RyuQueue import *
from shared.LCAction import *
from shared.LCFields import *
from time import sleep
from ryu.ofproto.ofproto_v1_3_parser import *


class RyuTranslateInit(unittest.TestCase):
    

    def atest_basic_init(self):
        translate = RyuTranslateInterface()


class RyuTranslateTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Setup RyuControllerInterface, which sets up RyuTranslateInterface
        cls.ctlrint = RyuControllerInterface()
        cls.trans = None
        cp = RyuCrossPollinate()
        while(cp.TranslateInterface == None):
            # Wait for cross pollination
            print "Waiting for cross pollination" 
            sleep(1)
        cls.trans = cp.TranslateInterface

        # Setup the virtual switch
        subprocess.call(['ovs-vsctl', 'add-br', 'br_ovs'])
        subprocess.call(['ovs-vsctl', 'add-port', 'br_ovs', 'vi0', '--', 'set', 'Interface', 'vi0', 'type=internal'])
        subprocess.call(['ovs-vsctl', 'set', 'bridge', 'br_ovs', 'other-config:datapath-id=0000000000000001'])
        subprocess.call(['ovs-vsctl', 'set-controller', 'br_ovs', 'tcp:127.0.0.1:6633'])


        # Wait for switch to connect to controller
        while(len(cls.trans.datapaths.keys()) == 0):
            print "Waiting " + str(cls.trans.datapaths)
            sleep(1)

        print "Datapaths: " + str(cls.trans.datapaths.keys())
        cls.datapath = cls.trans.datapaths[cls.trans.datapaths.keys()[0]]

    @classmethod
    def tearDownClass(cls):
        # Delete virtual switch
        subprocess.call(['ovs-vsctl', 'del-br', 'br_ovs'])

    ######################## TRANSLATE MATCH TESTS #########################
    def trans_test(self, ofm, ofpm):
        match_to_translate = OpenFlowMatch([ofm])
        translated_match = self.trans.translate_match(self.datapath, match_to_translate)
        prototype_match = OFPMatch(**ofpm)

        self.failUnlessEqual(str(translated_match), str(prototype_match))        

    def test_trans_match_IN_PORT(self):
        self.trans_test(IN_PORT(1), {'in_port':1})

    def test_trans_match_ETH_DST(self):
        self.trans_test(ETH_DST("00:00:00:00:00:01"), {'eth_dst':"00:00:00:00:00:01"})

    def test_trans_match_ETH_SRC(self):
        self.trans_test(ETH_SRC("00:00:00:00:00:02"), {'eth_src':"00:00:00:00:00:02"})

    def test_trans_match_IP_PROTO(self):
        self.trans_test(IP_PROTO(6), {'ip_proto':6})

    def test_trans_match_IPV4_SRC(self):
        self.trans_test(IPV4_SRC("1.2.3.4"), {'ipv4_src':"1.2.3.4"})

    def test_trans_match_IPV4_DST(self):
        self.trans_test(IPV4_DST("2.3.4.5"), {'ipv4_dst':"2.3.4.5"})

    def test_trans_match_IPV6_SRC(self):
        self.trans_test(IPV6_SRC("2001:0db8:0000:0042:0000:8a2e:0370:7334"), 
                        {'ipv6_src':"2001:0db8:0000:0042:0000:8a2e:0370:7334"})

    def test_trans_match_IPV6_DST(self):
        self.trans_test(IPV6_DST("2001:0db8:0000:0042:0000:8a2e:0370:7335"), 
                        {'ipv6_dst':"2001:0db8:0000:0042:0000:8a2e:0370:7335"})

    def test_trans_match_TCP_SRC(self):
        self.trans_test(TCP_SRC(6), {'tcp_src':6})

    def test_trans_match_TCP_DST(self):
        self.trans_test(TCP_DST(7), {'tcp_dst':7})

    def test_trans_match_UDP_SRC(self):
        self.trans_test(UDP_SRC(8), {'udp_src':8})

    def test_trans_match_UDP_DST(self):
        self.trans_test(UDP_DST(9), {'udp_dst':9})


    def trans_bad_test(self, ofm, ofpm):
        match_to_translate = OpenFlowMatch([ofm])
        translated_match = self.trans.translate_match(self.datapath, match_to_translate)
        prototype_match = OFPMatch(**ofpm)

        self.failIfEqual(str(translated_match), str(prototype_match))        

    def test_trans_match_bad_IN_PORT(self):
        self.trans_bad_test(IN_PORT(1), {'in_port':2})

    def test_trans_match_bad_ETH_DST(self):
        self.trans_bad_test(ETH_DST("00:00:00:00:00:01"), {'eth_dst':"00:00:00:00:00:02"})

    def test_trans_match_bad_ETH_SRC(self):
        self.trans_bad_test(ETH_SRC(0x000000000002), {'eth_src':"00:00:00:00:00:01"})

    def test_trans_match_bad_IP_PROTO(self):
        self.trans_bad_test(IP_PROTO(6), {'ip_proto':7})

    def test_trans_match_bad_IPV4_SRC(self):
        self.trans_bad_test(IPV4_SRC("1.2.3.4"), {'ipv4_src':"1.2.3.5"})

    def test_trans_match_bad_IPV4_DST(self):
        self.trans_bad_test(IPV4_DST("2.3.4.5"), {'ipv4_dst':"2.3.4.4"})

    def test_trans_match_bad_IPV6_SRC(self):
        self.trans_bad_test(IPV6_SRC("2001:0db8:0000:0042:0000:8a2e:0370:7334"), 
                            {'ipv6_src':"2001:0db8:0000:0042:0000:8a2e:0370:7335"})

    def test_trans_match_bad_IPV6_DST(self):
        self.trans_bad_test(IPV6_DST("2001:0db8:0000:0042:0000:8a2e:0370:7335"), 
                            {'ipv6_dst':"2001:0db8:0000:0042:0000:8a2e:0370:7334"})

    def test_trans_match_bad_TCP_SRC(self):
        self.trans_bad_test(TCP_SRC(6), {'tcp_src':7})

    def test_trans_match_bad_TCP_DST(self):
        self.trans_bad_test(TCP_DST(7), {'tcp_dst':8})

    def test_trans_match_bad_UDP_SRC(self):
        self.trans_bad_test(UDP_SRC(8), {'udp_src':9})

    def test_trans_match_bad_UDP_DST(self):
        self.trans_bad_test(UDP_DST(9), {'udp_dst':6})


    def trans_test_multi(self, ofm, ofpm):
        match_to_translate = OpenFlowMatch(ofm)
        translated_match = self.trans.translate_match(self.datapath, match_to_translate)
        prototype_match = OFPMatch(**ofpm)

        self.failUnlessEqual(str(translated_match), str(prototype_match))  

    def test_trans_double_match(self):
        self.trans_test_multi([IP_PROTO(6), TCP_SRC(1234)], {'ip_proto':6, 'tcp_src':1234})


    def trans_bad_test_multi(self, ofm, ofpm):
        match_to_translate = OpenFlowMatch(ofm)
        translated_match = self.trans.translate_match(self.datapath, match_to_translate)
        prototype_match = OFPMatch(**ofpm)

        self.failIfEqual(str(translated_match), str(prototype_match))       

    def test_trans_bad_double_match1(self):
        self.trans_bad_test_multi([IP_PROTO(6), TCP_SRC(1234)], {'ip_proto':5, 'tcp_src':1234})

    def test_trans_bad_double_match2(self):
        self.trans_bad_test_multi([IP_PROTO(6), TCP_SRC(1234)], {'ip_proto':6, 'tcp_src':1235})

    def test_trans_bad_double_match3(self):
        self.trans_bad_test_multi([IP_PROTO(6), TCP_SRC(1234)], {'ip_proto':5, 'tcp_src':1235})


    ######################## TRANSLATE ACTION TESTS #########################

    def test_trans_action_output_test(self):
        action_to_translate = action_OUTPUT(1)
        translated_action = self.trans.translate_action(self.datapath, action_to_translate)
        prototype_action = OFPActionOutput(1)

        self.failUnlessEqual(str(translated_action), str(prototype_action))

    def test_trans_action_set_field_test(self):
        action_to_translate = action_SET_FIELD(IP_PROTO(6))
        translated_action = self.trans.translate_action(self.datapath, action_to_translate)
        prototype_action = OFPActionSetField(ip_proto=6)

        self.failUnlessEqual(str(translated_action), str(prototype_action))

    #FIXME - need action tests
    
    ######################## TRANSLATE INSTRUCTION TESTS #########################
    
    def test_trans_instruction_GOTO_TABLE_test(self):
        instruction_to_translate = instruction_GOTO_TABLE(2)
        translated_instruction = self.trans.translate_instruction(self.datapath, instruction_to_translate)
        prototype_instruction = OFPInstructionGotoTable(2)

        self.failUnlessEqual(str(translated_instruction), str(prototype_instruction))

    def test_trans_instruction_WRITE_METADATA_test(self):
        instruction_to_translate = instruction_WRITE_METADATA(12345)
        translated_instruction = self.trans.translate_instruction(self.datapath, instruction_to_translate)
        prototype_instruction = OFPInstructionWriteMetadata(12345, 0xffffffffffffffff)

        self.failUnlessEqual(str(translated_instruction), str(prototype_instruction))

    def test_trans_instruction_WRITE_ACTIONS_test(self):
        actionlist = [action_SET_FIELD(IP_PROTO(6)),
                      action_OUTPUT(3)]
        instruction_to_translate = instruction_WRITE_ACTIONS(actionlist)
        translated_instruction = self.trans.translate_instruction(self.datapath, instruction_to_translate)
        prototype_instruction = OFPInstructionActions(ofproto.OFPIT_WRITE_ACTIONS,
                                                      [OFPActionSetField(ip_proto=6),
                                                       OFPActionOutput(3)])

        self.failUnlessEqual(str(translated_instruction), str(prototype_instruction))

    def test_trans_instruction_APPLY_ACTIONS_test(self):
        actionlist = [action_SET_FIELD(IP_PROTO(6)),
                      action_OUTPUT(3)]
        instruction_to_translate = instruction_APPLY_ACTIONS(actionlist)
        translated_instruction = self.trans.translate_instruction(self.datapath, instruction_to_translate)
        prototype_instruction = OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                                      [OFPActionSetField(ip_proto=6),
                                                       OFPActionOutput(3)])

        self.failUnlessEqual(str(translated_instruction), str(prototype_instruction))

    def test_trans_instruction_CLEAR_ACTIONS_test(self):
        instruction_to_translate = instruction_CLEAR_ACTIONS()
        translated_instruction = self.trans.translate_instruction(self.datapath, instruction_to_translate)
        # The empty list is due to a bug in ofproto_v1_3_parser.py:2758
        prototype_instruction = OFPInstructionActions(ofproto.OFPIT_CLEAR_ACTIONS,[]) 

        self.failUnlessEqual(str(translated_instruction), str(prototype_instruction))

if __name__ == '__main__':
    unittest.main()
