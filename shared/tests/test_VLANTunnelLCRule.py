# Copyright 2019 - Sean Donovan
# AlanticWave/SDX Project


# Unit tests for shared.VLANTunnelLCRule

import unittest
from shared.VlanTunnelLCRule import *

class BasicLCRuleTest(unittest.TestCase):

    def test_BasicLCRule(self):
        lcrule1 = VlanTunnelLCRule(1,2,3,4,5)

        self.assertEquals(1, lcrule1.get_switch_id())
        self.assertEquals(2, lcrule1.get_inport())
        self.assertEquals(3, lcrule1.get_outport())
        self.assertEquals(4, lcrule1.get_vlan_in())
        self.assertEquals(5, lcrule1.get_vlan_out())
        self.assertEquals(True, lcrule1.get_bidirectional())
        self.assertEquals(None, lcrule1.get_bandwidth())
        self.assertEqual("VlanTunnelLCRule: switch 1, None:2:3:4:5:True:None",
                         str(lcrule1))
        
        lcrule2 = VlanTunnelLCRule(1,2,3,4,5,False,1000)
        self.assertEquals(1, lcrule2.get_switch_id())
        self.assertEquals(2, lcrule2.get_inport())
        self.assertEquals(3, lcrule2.get_outport())
        self.assertEquals(4, lcrule2.get_vlan_in())
        self.assertEquals(5, lcrule2.get_vlan_out())
        self.assertEquals(False, lcrule2.get_bidirectional())
        self.assertEquals(1000, lcrule2.get_bandwidth())
        self.assertEqual("VlanTunnelLCRule: switch 1, None:2:3:4:5:False:1000",
                         str(lcrule2))

    def test_LCRuleEquality(self):
        lcrule1 = VlanTunnelLCRule(1,2,3,4,5,False,1000)
        lcrule2 = VlanTunnelLCRule(1,2,3,4,5,False,1000)
        lcrule3 = VlanTunnelLCRule(9,2,3,4,5,False,1000)
        lcrule4 = VlanTunnelLCRule(1,9,3,4,5,False,1000)
        lcrule5 = VlanTunnelLCRule(1,2,9,4,5,False,1000)
        lcrule6 = VlanTunnelLCRule(1,2,3,9,5,False,1000)
        lcrule7 = VlanTunnelLCRule(1,2,3,4,9,False,1000)
        lcrule8 = VlanTunnelLCRule(1,2,3,4,5, True,1000)
        lcrule9 = VlanTunnelLCRule(1,2,3,4,5,False,9000)
        

        self.assertEqual(lcrule1, lcrule2)
        self.assertNotEqual(lcrule1, lcrule3)
        self.assertNotEqual(lcrule1, lcrule4)
        self.assertNotEqual(lcrule1, lcrule5)
        self.assertNotEqual(lcrule1, lcrule6)
        self.assertNotEqual(lcrule1, lcrule7)
        self.assertNotEqual(lcrule1, lcrule8)
        self.assertNotEqual(lcrule1, lcrule9)


    def test_parsing_error_conditions(self):
        lcrule1 = VlanTunnelLCRule(1,2,3,4,5,False,1000)
        
        # inport
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,
                              'a', # Must be an int
                              3,4,5,False,1000)
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,
                              (1,2), # Must be an int
                              3,4,5,False,1000)
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,
                              [1], # Must be an int
                              3,4,5,False,1000)

        # outport
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,2,
                              'a', # Must be an int
                              4,5,False,1000)
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,2,
                              (1,2), # Must be an int
                              4,5,False,1000)
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,2,
                              [1], # Must be an int
                              4,5,False,1000)

        # vlan_in
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,2,3,
                              'a', # Must be an int
                              5,False,1000)
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,2,3,
                              (1,2), # Must be an int
                              5,False,1000)
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,2,3,
                              [1], # Must be an int
                              5,False,1000)

        # vlan_out
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,2,3,4,
                              'a', # Must be an int
                              False,1000)
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,2,3,4,
                              (1,2), # Must be an int
                              False,1000)
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,2,3,4,
                              [1], # Must be an int
                              False,1000)
        
        # bidirectional
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,2,3,4,5,
                              [1], # Must be an Boolean
                              1000)
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,2,3,4,5,
                              1, # Must be an Boolean
                              1000)
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,2,3,4,5,
                              'a', # Must be an Boolean
                              1000)

        # bandwidth
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,2,3,4,5,False,
                              [1]) # Must be an int
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,2,3,4,5,False,
                              1.1) # Must be an int
        self.failUnlessRaises(LCRuleTypeError, VlanTunnelLCRule,
                              1,2,3,4,5,False,
                              'a') # Must be an int
if __name__ == '__main__':
    unittest.main()
