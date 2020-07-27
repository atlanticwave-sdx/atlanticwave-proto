from __future__ import unicode_literals
# Copyright 2019 - Sean Donovan
# AlanticWave/SDX Project


# Unit tests for shared.L2MultipointLearnedDestinationLCRule

from builtins import str
import unittest
from shared.L2MultipointLearnedDestinationLCRule import *

class BasicLCRuleTest(unittest.TestCase):

    def test_BasicLCRule(self):
        lcrule1 = L2MultipointLearnedDestinationLCRule(1,'aa:bb:cc:dd:ee',
                                                       2, 1000, 100)

        self.assertEqual(1, lcrule1.get_switch_id())
        self.assertEqual('aa:bb:cc:dd:ee', lcrule1.get_dst_address())
        self.assertEqual(2, lcrule1.get_outport())
        self.assertEqual(1000, lcrule1.get_intermediate_vlan())
        self.assertEqual(100, lcrule1.get_out_vlan())
        self.assertEqual("L2MultipointLearnedDestinationLCRule: switch 1, None:aa:bb:cc:dd:ee:2",
                         str(lcrule1))

    def test_LCRuleEquality(self):
        lcrule1 = L2MultipointLearnedDestinationLCRule(1,'aa:bb:cc:dd:ee',
                                                       2, 1000, 100)
        lcrule2 = L2MultipointLearnedDestinationLCRule(1,'aa:bb:cc:dd:ee',
                                                       2, 1000, 100)
        lcrule3 = L2MultipointLearnedDestinationLCRule(2,'aa:bb:cc:dd:ee',
                                                       2, 1000, 100)
        lcrule4 = L2MultipointLearnedDestinationLCRule(1,'aa:bb:cc:dd:ff',
                                                       2, 1000, 100)
        lcrule5 = L2MultipointLearnedDestinationLCRule(1,'aa:bb:cc:dd:ee',
                                                       32, 1000, 100)
        lcrule6 = L2MultipointLearnedDestinationLCRule(1,'aa:bb:cc:dd:ee',
                                                       2, 2000, 100)
        lcrule7 = L2MultipointLearnedDestinationLCRule(1,'aa:bb:cc:dd:ee',
                                                       2, 1000, 200)
        

        self.assertEqual(lcrule1, lcrule2)
        self.assertNotEqual(lcrule1, lcrule3)
        self.assertNotEqual(lcrule1, lcrule4)
        self.assertNotEqual(lcrule1, lcrule5)
        self.assertNotEqual(lcrule1, lcrule6)
        self.assertNotEqual(lcrule1, lcrule7)


    def test_parsing_error_conditions(self):
        L2MultipointLearnedDestinationLCRule(1,'aa:bb:cc:dd:ee',
                                             2, 1000, 100)

        # outport - must be an int
        self.assertRaises(LCRuleTypeError,
                              L2MultipointLearnedDestinationLCRule,
                              1, 'aa:bb:cc:dd:ee',
                              'a', # Must be an int
                              1000, 100)
        self.assertRaises(LCRuleTypeError,
                              L2MultipointLearnedDestinationLCRule,
                              1, 'aa:bb:cc:dd:ee',
                              (1,2), # Must be an int
                              1000, 100)
        self.assertRaises(LCRuleTypeError,
                              L2MultipointLearnedDestinationLCRule,
                              1, 'aa:bb:cc:dd:ee',
                              [1], # Must be an int
                              1000, 100)
        
        # intermediate_vlan - must be an int.
        self.assertRaises(LCRuleTypeError,
                              L2MultipointLearnedDestinationLCRule,
                              1, 'aa:bb:cc:dd:ee', 2,
                              'a', # Must be an int
                              100)
        self.assertRaises(LCRuleTypeError,
                              L2MultipointLearnedDestinationLCRule,
                              1, 'aa:bb:cc:dd:ee', 2,
                              (1,2), # Must be an int
                              100)
        self.assertRaises(LCRuleTypeError,
                              L2MultipointLearnedDestinationLCRule,
                              1, 'aa:bb:cc:dd:ee', 2,
                              [1], # Must be an int
                              100)

        # out_vlan - must be an int.
        self.assertRaises(LCRuleTypeError,
                              L2MultipointLearnedDestinationLCRule,
                              1, 'aa:bb:cc:dd:ee', 2, 1000,
                              'a') # Must be an int
        self.assertRaises(LCRuleTypeError,
                              L2MultipointLearnedDestinationLCRule,
                              1, 'aa:bb:cc:dd:ee', 2, 1000,
                              (1,2)) # Must be an int
        self.assertRaises(LCRuleTypeError,
                              L2MultipointLearnedDestinationLCRule,
                              1, 'aa:bb:cc:dd:ee', 2, 1000,
                              [1]) # Must be an int

        
if __name__ == '__main__':
    unittest.main()
