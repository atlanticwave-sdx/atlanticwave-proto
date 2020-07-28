from __future__ import unicode_literals
# Copyright 2019 - Sean Donovan
# AlanticWave/SDX Project


# Unit tests for shared.MatchActionLCRule

from builtins import str
import unittest
from shared.MatchActionLCRule import *
from shared.LCFields import *
from shared.LCAction import *

class BasicLCRuleTest(unittest.TestCase):

    def test_BasicLCRule(self):
        lcmatch = TCP_SRC(3)
        lcaction = SetField(TCP_SRC(4))
        lcrule1 = MatchActionLCRule(1, [lcmatch], [lcaction])

        self.assertEqual(1, lcrule1.get_switch_id())
        self.assertEqual([lcmatch], lcrule1.get_matches())
        self.assertEqual([lcaction], lcrule1.get_actions())
        self.assertEqual(True, lcrule1.get_ingress())
        self.assertEqual("MatchActionLCRule: switch1:None:True\n    [TCP_SRC : tcp_src:3 False]\n    [SetField:tcp_src:4]",
                         str(lcrule1))

        lcrule2 = MatchActionLCRule(1, [], [lcaction])
        lcrule3 = MatchActionLCRule(1, [lcmatch], [])
        lcrule4 = MatchActionLCRule(1, [], [])
        lcrule4 = MatchActionLCRule(1, [], [], True)
        lcrule4 = MatchActionLCRule(1, [], [], False)


    def test_LCRuleEquality(self):
        lcmatch = TCP_SRC(3)
        lcaction = SetField(TCP_SRC(4))
        lcrule1 = MatchActionLCRule(1, [lcmatch], [lcaction])
        lcrule2 = MatchActionLCRule(1, [lcmatch], [lcaction])
        lcrule3 = MatchActionLCRule(2, [lcmatch], [lcaction])
        lcrule4 = MatchActionLCRule(1, [], [lcaction])
        lcrule5 = MatchActionLCRule(1, [lcmatch], [])
        lcrule6 = MatchActionLCRule(1, [TCP_DST(3)], [lcaction])
        lcrule7 = MatchActionLCRule(1, [lcmatch], [WriteMetadata(100)])
        
        
        self.assertEqual(lcrule1, lcrule2)
        self.assertNotEqual(lcrule1, lcrule3)
        self.assertNotEqual(lcrule1, lcrule4)
        self.assertNotEqual(lcrule1, lcrule5)
        self.assertNotEqual(lcrule1, lcrule6)
        self.assertNotEqual(lcrule1, lcrule7)


    def test_parsing_error_conditions(self):
        lcmatch = TCP_SRC(3)
        lcaction = SetField(TCP_SRC(4))
        lcrule1 = MatchActionLCRule(1, [lcmatch], [lcaction])


        # matches
        self.assertRaises(LCRuleTypeError, MatchActionLCRule,
                              1,
                              [lcaction], # Must be a list of LCFields
                              [lcaction])
        self.assertRaises(LCRuleTypeError, MatchActionLCRule,
                              1,
                              lcmatch, # Must be a list of LCFields
                              [lcaction])
        self.assertRaises(LCRuleTypeError, MatchActionLCRule,
                              1,
                              [1,2,3], # Must be a list of LCFields
                              [lcaction])
        
        # Actions
        self.assertRaises(LCRuleTypeError, MatchActionLCRule,
                              1, [lcmatch],
                              [lcmatch]) # Must be a list of LCActions
        self.assertRaises(LCRuleTypeError, MatchActionLCRule,
                              1, [lcmatch],
                              lcaction) # Must be a list of LCActions
        self.assertRaises(LCRuleTypeError, MatchActionLCRule,
                              1, [lcmatch],
                              [1,2,3]) # Must be a list of LCActions

        # ingress
        self.assertRaises(LCRuleTypeError, MatchActionLCRule,
                              1, [lcmatch], [lcaction],
                              1) # Must be boolean
if __name__ == '__main__':
    unittest.main()
