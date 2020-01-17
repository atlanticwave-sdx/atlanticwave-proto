# Copyright 2019 - Sean Donovan
# AlanticWave/SDX Project


# Unit tests for shared.FloodTreeLCRule

import unittest
from shared.FloodTreeLCRule import *

class BasicLCRuleTest(unittest.TestCase):

    def test_BasicLCRule(self):
        lcrule1 = FloodTreeLCRule(1,[1,2,3])

        self.assertEqual(1, lcrule1.get_switch_id())
        self.assertEqual([1,2,3], lcrule1.get_ports())
        self.assertEqual("FloodTreeLCRule: switch 1, None, ([1, 2, 3])",
                         str(lcrule1))

    def test_LCRuleEquality(self):
        lcrule1 = FloodTreeLCRule(1,[1,2,3])
        lcrule2 = FloodTreeLCRule(1,[1,2,3])
        lcrule3 = FloodTreeLCRule(2,[1,2,3])
        lcrule4 = FloodTreeLCRule(2,[1,2,3,4])
        lcrule5 = FloodTreeLCRule(1,[2,3])
        lcrule6 = FloodTreeLCRule(1,[2,3,4])
        

        lcrule1 == lcrule2
        self.assertEqual(lcrule1, lcrule2)
        self.assertNotEqual(lcrule1, lcrule3)
        self.assertNotEqual(lcrule1, lcrule4)
        self.assertNotEqual(lcrule1, lcrule5)
        self.assertNotEqual(lcrule1, lcrule6)

if __name__ == '__main__':
    unittest.main()
