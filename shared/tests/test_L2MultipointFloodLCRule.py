from __future__ import unicode_literals
# Copyright 2019 - Sean Donovan
# AlanticWave/SDX Project


# Unit tests for shared.L2MultipointFloodLCRule

from builtins import str
import unittest
from shared.L2MultipointFloodLCRule import *

class BasicLCRuleTest(unittest.TestCase):

    def test_BasicLCRule(self):
        lcrule1 = L2MultipointFloodLCRule(1,[1,2,3], 1000)

        self.assertEqual(1, lcrule1.get_switch_id())
        self.assertEqual([1,2,3], lcrule1.get_flooding_ports())
        self.assertEquals(1000, lcrule1.get_intermediate_vlan())
        self.assertEqual("L2MultipointFloodLCRule: switch 1, None:([1, 2, 3]), 1000",
                         str(lcrule1))

    def test_LCRuleEquality(self):
        lcrule1 = L2MultipointFloodLCRule(1,[1,2,3],1000)
        lcrule2 = L2MultipointFloodLCRule(1,[1,2,3],1000)
        lcrule3 = L2MultipointFloodLCRule(2,[1,2,3],1000)
        lcrule4 = L2MultipointFloodLCRule(1,[2,3],1000)
        lcrule5 = L2MultipointFloodLCRule(1,[2,3,4],1000)
        lcrule6 = L2MultipointFloodLCRule(1,[1,2,3],2000)
        

        self.assertEqual(lcrule1, lcrule2)
        self.assertNotEqual(lcrule1, lcrule3)
        self.assertNotEqual(lcrule1, lcrule4)
        self.assertNotEqual(lcrule1, lcrule5)
        self.assertNotEqual(lcrule1, lcrule6)


    def test_parsing_error_conditions(self):
        L2MultipointFloodLCRule(1,[1,2,3],1000)

        # flooding_port
        self.assertRaises(LCRuleTypeError, L2MultipointFloodLCRule,
                              1,
                              ['a','b','c'], # Must be a list of ints or None
                              1000)
        self.assertRaises(LCRuleTypeError, L2MultipointFloodLCRule,
                              1,
                              2, # Must be a list of ints or None
                              1000)
        
        # intermediate_vlan - must be None or an int.
        self.assertRaises(LCRuleTypeError, L2MultipointFloodLCRule,
                              1,[1,2,3],
                              'a') # Must be an int 
        self.assertRaises(LCRuleTypeError, L2MultipointFloodLCRule,
                              1,[1,2,3],
                              None) # Must be an int
        self.assertRaises(LCRuleTypeError, L2MultipointFloodLCRule,
                              1,[1,2,3],
                              (1,2)) # Must be an int 
        self.assertRaises(LCRuleTypeError, L2MultipointFloodLCRule,
                              1,[1,2,3],
                              [1]) # Must be an int 


        
if __name__ == '__main__':
    unittest.main()
