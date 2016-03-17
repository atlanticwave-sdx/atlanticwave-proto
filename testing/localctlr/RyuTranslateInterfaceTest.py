# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for RyuTranslateInterfaace

import unittest
import mock
from localctlr.RyuTranslateInterface import *
from localctlr.RyuControllerInterface import *
from localctlr.RyuQueue import *
from shared.match import *
from shared.offield import *
from time import sleep
from ryu.ofproto.ofproto_v1_3_parser import OFPMatch, OFPAction


class RyuTranslateInit(unittest.TestCase):
    

    def atest_basic_init(self):
        translate = RyuTranslateInterface()


class RyuTranslateTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ctlrint = RyuControllerInterface()
        cls.trans = None
        cp = RyuCrossPollinate()
        while(cp.TranslateInterface == None):
            # Wait for cross pollination
            print "Waiting for cross pollination" 
            sleep(1)
        cls.trans = cp.TranslateInterface


        # WHY ISN"T THIS SIGNLETON WORKING? I WANT TO MANUALLY GET THIS>>>>
        # RyuTranslateInterface inherits from something that's not a singleton. This is why it's not working. need to figure out a way to handle that. Singleton internal data structure? 
        while(len(cls.trans.datapaths.keys()) == 0):
            print "Waiting " + str(cls.trans.datapaths)
            sleep(1)

        print "Datapaths: " + str(cls.trans.datapaths.keys())
        cls.datapath = cls.trans.datapaths[cls.trans.datapaths.keys()[0]]


    ######################## TRANSLATE MATCH TESTS #########################
    def trans_test(self, ofm, ofpm):
        match_to_translate = OpenFlowMatch([ofm])
        translated_match = self.trans.translate_match(self.datapath, match_to_translate)
        prototype_match = OFPMatch(**ofpm)

        self.failUnlessEqual(str(translated_match), str(prototype_match))        

    def test_trans_match_IN_PORT(self):
        self.trans_test(IN_PORT(1), {'in_port':1})

    def test_trans_match_ETH_DST(self):
        self.trans_test(ETH_DST(0x000000000001), {'eth_dst':"00:00:00:00:00:01"})

    def test_trans_match_ETH_SRC(self):
        self.trans_test(ETH_SRC(0x000000000002), {'eth_src':"00:00:00:00:00:02"})

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
        self.trans_bad_test(ETH_DST(0x000000000001), {'eth_dst':"00:00:00:00:00:02"})

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

    def trans_action_output_test(self, ofa, ofpa):
        action_to_translate = OpenFlowAction([ofa])
        translated_action = self.trans.translate_action(self.datapath, action_to_translate)
        prototype_action = OFPActionOutput(ofpa)

        self.FailUnlessEqual(str(translated_action), str(prototype_action))

    def trans_action_set_field_test(self, ofa, ofpa):
        action_to_translate = OpenFlowAction([ofa])
        translated_action = self.trans.translate_action(self.datapath, action_to_translate)
        prototype_action = OFPActionSetField(ofpa)

        self.FailUnlessEqual(str(translated_action), str(prototype_action))

    
    ######################## TRANSLATE INSTRUCTION TESTS #########################
    
    

if __name__ == '__main__':
    unittest.main()
