# Copyright 2019 - Sean Donovan
# AtlanticWave/SDX Project


# Unittests for shared.LCRule module

import unittest
from shared.LCRule import *


class BasicLCRuleTests(unittest.TestCase):
    def test_init(self):
        lc1 = LCRule(1)
        lc2 = LCRule(2,'asdf')
        #Make sure it doesn't blow up.

    def test_get_methods(self):
        lc1 = LCRule(1)
        lc2 = LCRule(2,'asdf')

        self.assertEqual(lc1.get_switch_id(), 1)
        self.assertEqual(lc1.get_cookie(), None)

        self.assertEqual(lc2.get_switch_id(), 2)
        self.assertEqual(lc2.get_cookie(), 'asdf')
    

    def test_set_method(self):
        lc1 = LCRule(1)
        self.assertEqual(lc1.get_switch_id(), 1)
        self.assertEqual(lc1.get_cookie(), None)

        lc1.set_cookie("qwer")
        self.assertEqual(lc1.get_switch_id(), 1)
        self.assertEqual(lc1.get_cookie(), 'qwer')

    def test_equality(self):
        lc1 = LCRule(1, "er")
        lc2 = LCRule(1, "er")
        lc3 = LCRule(2, "er")
        lc4 = LCRule(1, "erq")

        self.assertEqual(lc1, lc2)
        self.assertNotEqual(lc1, lc3)
        self.assertNotEqual(lc1, lc3)
        self.assertNotEqual(lc1, None)




if __name__ == '__main__':
    unittest.main()
