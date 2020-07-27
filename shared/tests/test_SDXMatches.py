from __future__ import unicode_literals
# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Proejct


# Unit tests for shared.SDXMatches module

import unittest
from shared.LCFields import LCField
from shared.SDXMatches import *


class BasicMatchTest(unittest.TestCase):
    def test_basic_init(self):
        lcfield = LCField('field')
        a_match = SDXMatch("a", 6, lcfield)
        return

    def test_no_lcfield_init(self):
        try:
            a_match = SDXMatch("a", 6, "not an lcfield")
        except TypeError:
            pass
        else:
            self.fail("did not see error")

    def test_equality(self):
        a_field = LCField('field')
        a_match = SDXMatch("a", 6, a_field)
        b_field = LCField('field')
        b_match = SDXMatch("a", 6, b_field)
        self.assertEqual(a_match, b_match)

    def test_lookup(self):
        self.assertEqual(type(SDXMatchSRCMAC),
                             type(SDXMatch.lookup_match_type("src_mac")))

    def test_failed_lookup(self):
        try:
            t = SDXMatch.lookup_match_type("NOT_A_THING!")
        except ValueError:
            pass
        else:
            self.fail("did not see error")
        



if __name__ == '__main__':
    unittest.main()
