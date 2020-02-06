# Copyright 2019 - Sean Donovan
# AlanticWave/SDX Project


# Unit tests for shared.ManagementVLANLCRule
### Hard Coded in ManagementVLANLCRule.py
###MANAGEMENT_VLAN_MIN = 1401
###MANAGEMENT_VLAN_MAX = 1415
import unittest
from shared.ManagementVLANLCRule import *

TEST_VLAN=(MANAGEMENT_VLAN_MIN+MANAGEMENT_VLAN_MAX)/2
class BasicLCRuleTest(unittest.TestCase):

    def test_BasicLCRule(self):
        lcrule1 = ManagementVLANLCRule(1, TEST_VLAN, [1,2], [3])

        self.assertEqual(1, lcrule1.get_switch_id())
        self.assertEqual(TEST_VLAN, lcrule1.get_mgmt_vlan())
        self.assertEqual([1,2], lcrule1.get_mgmt_vlan_ports())
        self.assertEqual([3], lcrule1.get_untagged_mgmt_vlan_ports())
        self.assertEqual("ManagementVLANLCRule: switch 1, None: %d, ([1, 2]), ([3])" % (TEST_VLAN),
                         str(lcrule1))

        lcrule2 = ManagementVLANLCRule(1, MANAGEMENT_VLAN_MIN, [], [3])
        lcrule3 = ManagementVLANLCRule(1, MANAGEMENT_VLAN_MIN+1, [1,2], [])
        lcrule4 = ManagementVLANLCRule(1, MANAGEMENT_VLAN_MAX, [], [])


    def test_LCRuleEquality(self):
        lcrule1 = ManagementVLANLCRule(1, TEST_VLAN, [1,2], [3])
        lcrule2 = ManagementVLANLCRule(1, TEST_VLAN, [1,2], [3])
        lcrule3 = ManagementVLANLCRule(1, TEST_VLAN+1, [1,2], [3])
        lcrule4 = ManagementVLANLCRule(1, TEST_VLAN, [1,2,3], [3])
        lcrule5 = ManagementVLANLCRule(1, TEST_VLAN, [1,2], [4])        

        self.assertEqual(lcrule1, lcrule2)
        self.assertNotEqual(lcrule1, lcrule3)
        self.assertNotEqual(lcrule1, lcrule4)
        self.assertNotEqual(lcrule1, lcrule5)


    def test_parsing_error_conditions(self):
        ManagementVLANLCRule(1, TEST_VLAN, [1,2], [3])

        # mgmt_vlan
        self.failUnlessRaises(LCRuleTypeError, ManagementVLANLCRule,
                              1,
                              'a', # Must be an int
                              [1,2],[3])
        self.failUnlessRaises(LCRuleTypeError, ManagementVLANLCRule,
                              1,
                              [1,2], # Must be an int
                              [1,2],[3])
        self.failUnlessRaises(LCRuleTypeError, ManagementVLANLCRule,
                              1,
                              (1,2), # Must be an int
                              [1,2],[3])
        self.failUnlessRaises(LCRuleValueError, ManagementVLANLCRule,
                              1,
                              0, # Must be between MANAGEMENT_VLAN_MIN and MANAGEMENT_VLAN_MAX
                              [1,2],[3])
        self.failUnlessRaises(LCRuleValueError, ManagementVLANLCRule,
                              1,
                              -1, # Must be between MANAGEMENT_VLAN_MIN and MANAGEMENT_VLAN_MAX
                              [1,2],[3])
        self.failUnlessRaises(LCRuleValueError, ManagementVLANLCRule,
                              1,
                              MANAGEMENT_VLAN_MAX+1, # Must be between MANAGEMENT_VLAN_MIN and MANAGEMENT_VLAN_MAX
                              [1,2],[3])
        self.failUnlessRaises(LCRuleValueError, ManagementVLANLCRule,
                              1,
                              MANAGEMENT_VLAN_MIN-1, # MANAGEMENT_VLAN_MIN and MANAGEMENT_VLAN_MAX
                              [1,2],[3])
        self.failUnlessRaises(LCRuleValueError, ManagementVLANLCRule,
                              1,
                              5000, # Must be between 1 and 4095
                              [1,2],[3])

        # mgmt_vlan_ports - List of numbers 
        self.failUnlessRaises(LCRuleTypeError, ManagementVLANLCRule,
                              1, TEST_VLAN,
                              [1,'a'], # must be list of numbers
                              [3])
        self.failUnlessRaises(LCRuleTypeError, ManagementVLANLCRule,
                              1, TEST_VLAN,
                              (1,2), # must be list of numbers
                              [3])
        self.failUnlessRaises(LCRuleTypeError, ManagementVLANLCRule,
                              1, TEST_VLAN,
                              12, # must be list of numbers
                              [3])

        # untagged_mgmt_vlan_ports - List of numbers 
        self.failUnlessRaises(LCRuleTypeError, ManagementVLANLCRule,
                              1, TEST_VLAN, [1,2],
                              [1,'a']) # must be list of numbers
        self.failUnlessRaises(LCRuleTypeError, ManagementVLANLCRule,
                              1, TEST_VLAN, [1,2],
                              (1,2)) # must be list of numbers
        self.failUnlessRaises(LCRuleTypeError, ManagementVLANLCRule,
                              1, TEST_VLAN, [1,2],
                              12) # must be list of numbers
if __name__ == '__main__':
    unittest.main()
