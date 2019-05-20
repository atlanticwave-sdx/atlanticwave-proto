# Copyright 2019 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for shared.SDXPolicy module


import unittest
from shared.SDXPolicy import *
#from shared.SDXMatches import *
#from shared.SDXActions import *

example_sdxpolicy_1 = {"SDX":
                       {"starttime":"1985-04-12T23:20:50",
                        "endtime":"1985-04-12T23:20:50",
                        "switch":"atl-switch",
                        "matches": [],
                        "actions": []}}
sdxpolicy_str = "SDX(1985-04-12T23:20:50,1985-04-12T23:20:50,atl-switch,[],[])"

example_sdxpolicy_2 = {"SDX":
                       {"starttime":"1985-04-12T23:20:50",
                        "endtime":"1985-04-12T23:20:50",
                        "switch":"atl-switch",
                        "matches": [{'src_mac':3}],
                        "actions": [{'Forward':4}]}}




example_ingress_1 = {"SDXIngress":
                     {"starttime":"1985-04-12T23:20:50",
                      "endtime":"1985-04-12T23:20:50",
                      "switch":"atl-switch",
                      "matches": [],
                      "actions": []}}
sdxingresspolicy_str = "SDXIngress(1985-04-12T23:20:50,1985-04-12T23:20:50,atl-switch,[],[])"

example_egress_1  = {"SDXEgress":
                     {"starttime":"1985-04-12T23:20:50",
                      "endtime":"1985-04-12T23:20:50",
                      "switch":"atl-switch",
                      "matches": [],
                      "actions": []}}
sdxegresspolicy_str = "SDXEgress(1985-04-12T23:20:50,1985-04-12T23:20:50,atl-switch,[],[])"

username = 'sdonovan'

class BasicSDXPolicyTest(unittest.TestCase):
    def test_init(self):
        sdxpol = SDXPolicy(username, example_sdxpolicy_1)
        self.assertEqual(str(sdxpol), sdxpolicy_str)

        # Make sure these don't blow up
        sdxpol.pre_add_callback(None, None)
        sdxpol.pre_remove_callback(None, None)
        sdxpol.switch_change_callback(None, None, None)

    def test_breakdown(self):
        sdxpol = SDXPolicy(username, example_sdxpolicy_2)
        #FIXME


class BasicSDXIngressPolicyTest(unittest.TestCase):
    def test_init(self):
        sdxpol = SDXIngressPolicy(username, example_ingress_1)
        self.assertEqual(str(sdxpol), sdxingresspolicy_str)

        # Make sure these don't blow up
        sdxpol.pre_add_callback(None, None)
        sdxpol.pre_remove_callback(None, None)
        sdxpol.switch_change_callback(None, None, None)

class BasicSDXEgressPolicyTest(unittest.TestCase):
    def test_init(self):
        sdxpol = SDXEgressPolicy(username, example_egress_1)
        self.assertEqual(str(sdxpol), sdxegresspolicy_str)

        # Make sure these don't blow up
        sdxpol.pre_add_callback(None, None)
        sdxpol.pre_remove_callback(None, None)
        sdxpol.switch_change_callback(None, None, None)


class ClassMethodsTest(unittest.TestCase):
    #check_syntax
    def test_SDXPolicy(self):
        SDXPolicy.check_syntax(example_sdxpolicy_1)
        
    def test_IngressPolicy(self):
        SDXIngressPolicy.check_syntax(example_ingress_1)

    def test_EgressPolicy(self):
        SDXEgressPolicy.check_syntax(example_egress_1)



if __name__ == '__main__':
    unittest.main()
