from __future__ import unicode_literals
# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Proejct


# Unit tests for shared.SDXActions module

import unittest
from shared.LCAction import LCAction
from shared.SDXActions import *


class BasicActionTest(unittest.TestCase):
    def test_basic_init(self):
        lcaction = LCAction("fakeaction")
        a_action = SDXAction("a", 6, lcaction)
        return

    def test_no_lcfield_init(self):
        try:
            a_action = SDXAction("a", 6, "not an lcaction")
        except TypeError:
            pass
        else:
            self.fail("did not see error")

    def test_equality(self):
        a_field = LCAction('field')
        a_match = SDXAction("a", 6, a_field)
        b_field = LCAction('field')
        b_match = SDXAction("a", 6, b_field)
        self.assertEqual(a_match, b_match)

    def test_lookup(self):
        self.assertEqual(type(SDXActionModifySRCMAC),
                             type(SDXAction.lookup_action_type("ModifySRCMAC")))

    def test_failed_lookup(self):
        try:
            t = SDXAction.lookup_action_type("NOT_A_THING!")
        except ValueError:
            pass
        else:
            self.fail("did not see error")
        



if __name__ == '__main__':
    unittest.main()
