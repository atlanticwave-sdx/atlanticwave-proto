# Copyright 2019 - Sean Donovan
# AlanticWave/SDX Project


# Unit tests for shared.LearnedDestinationLCRule

import unittest
from shared.LearnedDestinationLCRule import *

class BasicLCRuleTest(unittest.TestCase):

    def test_BasicLCRule(self):
        lcrule1 = LearnedDestinationLCRule(1,'aa:bb:cc:dd:ee', 2)

        self.assertEqual(1, lcrule1.get_switch_id())
        self.assertEqual('aa:bb:cc:dd:ee', lcrule1.get_dst_address())
        self.assertEqual(2, lcrule1.get_outport())
        self.assertEqual("LearnedDestinationLCRule: switch 1, None:aa:bb:cc:dd:ee:2",
                         str(lcrule1))

    def test_LCRuleEquality(self):
        lcrule1 = LearnedDestinationLCRule(1,'aa:bb:cc:dd:ee', 2)
        lcrule2 = LearnedDestinationLCRule(1,'aa:bb:cc:dd:ee', 2)
        lcrule3 = LearnedDestinationLCRule(2,'aa:bb:cc:dd:ee', 2)
        lcrule4 = LearnedDestinationLCRule(1,'aa:bb:cc:dd:ff', 2)
        lcrule5 = LearnedDestinationLCRule(1,'aa:bb:cc:dd:ee', 3)
        

        self.assertEqual(lcrule1, lcrule2)
        self.assertNotEqual(lcrule1, lcrule3)
        self.assertNotEqual(lcrule1, lcrule4)
        self.assertNotEqual(lcrule1, lcrule5)


    def test_parsing_error_conditions(self):
        LearnedDestinationLCRule(1,'aa:bb:cc:dd:ee', 2)

        # outport - must be an int
        self.failUnlessRaises(LCRuleTypeError, LearnedDestinationLCRule,
                              1, 'aa:bb:cc:dd:ee',
                              'a') # Must be an int
        self.failUnlessRaises(LCRuleTypeError, LearnedDestinationLCRule,
                              1, 'aa:bb:cc:dd:ee',
                              (1,2)) # Must be an int
        self.failUnlessRaises(LCRuleTypeError, LearnedDestinationLCRule,
                              1, 'aa:bb:cc:dd:ee',
                              [1]) # Must be an int


if __name__ == '__main__':
    unittest.main()
