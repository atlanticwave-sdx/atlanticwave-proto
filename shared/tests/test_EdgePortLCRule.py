# Copyright 2019 - Sean Donovan
# AlanticWave/SDX Project


# Unit tests for shared.EdgePortLCRule

import unittest
from shared.EdgePortLCRule import *
class BasicLCRuleTest(unittest.TestCase):

    def test_BasicLCRule(self):
        lcrule1 = EdgePortLCRule(1,2)
        lcrule4 = EdgePortLCRule(1,1)

        self.assertEqual(1, lcrule1.get_switch_id())
        self.assertEqual(2, lcrule1.get_edgeport())
        self.assertEqual("EdgePortLCRule: switch 1, None:2", str(lcrule1))

    def test_LCRuleEquality(self):
        lcrule1 = EdgePortLCRule(1,2)
        lcrule2 = EdgePortLCRule(1,2)
        lcrule3 = EdgePortLCRule(2,2)
        lcrule4 = EdgePortLCRule(1,1)

        self.assertEqual(lcrule1, lcrule2)
        self.assertNotEqual(lcrule1, lcrule3)
        self.assertNotEqual(lcrule1, lcrule4)
if __name__ == '__main__':
    unittest.main()
