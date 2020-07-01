from __future__ import unicode_literals
# Copyright 2019 - Sean Donovan
# AlanticWave/SDX Project


# Unit tests for shared.L2MultipointEndpointLCRule

from builtins import str
import unittest
from shared.L2MultipointEndpointLCRule import *

class BasicLCRuleTest(unittest.TestCase):

    def test_BasicLCRule(self):
        lcrule1 = L2MultipointEndpointLCRule(1,[1,2,3],[(4,100),(5,200)],
                                            1000, None)

        self.assertEqual(1, lcrule1.get_switch_id())
        self.assertEqual([1,2,3], lcrule1.get_flooding_ports())
        self.assertEqual([(4,100),(5,200)],
                          lcrule1.get_endpoint_ports_and_vlans())
        self.assertEqual(1000, lcrule1.get_intermediate_vlan())
        self.assertEqual(None, lcrule1.get_bandwidth())
        self.assertEqual("L2MultipointEndpointLCRule: switch 1, None:([1, 2, 3]), ([(4, 100), (5, 200)]), 1000, None",
                         str(lcrule1))

        lcrule2 = L2MultipointEndpointLCRule(1,[3],[(4,100)],
                                             1000, 100000)

        self.assertEqual(1, lcrule2.get_switch_id())
        self.assertEqual([3], lcrule2.get_flooding_ports())
        self.assertEqual([(4,100)],
                          lcrule2.get_endpoint_ports_and_vlans())
        self.assertEqual(1000, lcrule2.get_intermediate_vlan())
        self.assertEqual(100000, lcrule2.get_bandwidth())
        self.assertEqual("L2MultipointEndpointLCRule: switch 1, None:([3]), ([(4, 100)]), 1000, 100000",
                         str(lcrule2))

        lcrule3 = L2MultipointEndpointLCRule(1,[],[(4,100),(5,200)],
                                             1000, 100000)

        self.assertEqual(1, lcrule3.get_switch_id())
        self.assertEqual([], lcrule3.get_flooding_ports())
        self.assertEqual([(4,100),(5,200)],
                          lcrule3.get_endpoint_ports_and_vlans())
        self.assertEqual(1000, lcrule3.get_intermediate_vlan())
        self.assertEqual(100000, lcrule3.get_bandwidth())
        self.assertEqual("L2MultipointEndpointLCRule: switch 1, None:([]), ([(4, 100), (5, 200)]), 1000, 100000",
                         str(lcrule3))

        self.assertEqual(1, lcrule3.get_switch_id())
        self.assertEqual([], lcrule3.get_flooding_ports())
        self.assertEqual([(4,100),(5,200)],
                          lcrule3.get_endpoint_ports_and_vlans())
        self.assertEqual(1000, lcrule3.get_intermediate_vlan())
        self.assertEqual(100000, lcrule3.get_bandwidth())
        self.assertEqual("L2MultipointEndpointLCRule: switch 1, None:([]), ([(4, 100), (5, 200)]), 1000, 100000",
                         str(lcrule3))

    def test_LCRuleEquality(self):
        lcrule1 = L2MultipointEndpointLCRule(1,[1,2,3],[(4,100),(5,200)],
                                            1000, None)
        lcrule2 = L2MultipointEndpointLCRule(1,[1,2,3],[(4,100),(5,200)],
                                            1000, None)
        lcrule3 = L2MultipointEndpointLCRule(1,[1,2],[(4,100),(5,200)],
                                            1000, None)
        lcrule4 = L2MultipointEndpointLCRule(1,[1,2,3],[(6,100),(5,200)],
                                            1000, None)
        lcrule5 = L2MultipointEndpointLCRule(1,[1,2,3],[(4,101),(5,200)],
                                            1000, None)
        lcrule6 = L2MultipointEndpointLCRule(1,[1,2,3],
                                             [(4,100),(5,200),(6,300)],
                                             1000, None)
        lcrule7 = L2MultipointEndpointLCRule(1,[1,2,3],[(4,100),(5,200)],
                                            2000, None)
        lcrule8 = L2MultipointEndpointLCRule(1,[1,2,3],[(4,100),(5,200)],
                                            1000, 1000000)
        

        self.assertEqual(lcrule1, lcrule2)
        self.assertNotEqual(lcrule1, lcrule3)
        self.assertNotEqual(lcrule1, lcrule4)
        self.assertNotEqual(lcrule1, lcrule5)
        self.assertNotEqual(lcrule1, lcrule6)
        self.assertNotEqual(lcrule1, lcrule7)
        self.assertNotEqual(lcrule1, lcrule8)


    def test_parsing_error_conditions(self):
        lcrule1 = L2MultipointEndpointLCRule(1,[1,2,3],[(4,100),(5,200)],
                                            1000, None)

        # flooding_port
        self.assertRaises(LCRuleTypeError, L2MultipointEndpointLCRule,
                              1,
                              ['a','b','c'], # Must be a list of ints or None
                              [(4,100),(5,200)],1000, None)
        self.assertRaises(LCRuleTypeError, L2MultipointEndpointLCRule,
                              1,
                              2, # Must be a list of ints or None
                              [(4,100),(5,200)],1000, None)
        
        # endpoint_ports_and_vlans - list of tuples, cannot be None
        self.assertRaises(LCRuleTypeError, L2MultipointEndpointLCRule,
                              1,[1,2,3],
                              [4,100,5,200], # Must be list of tuples
                              1000, None)
        self.assertRaises(LCRuleTypeError, L2MultipointEndpointLCRule,
                              1,[1,2,3],
                              5, # Must be list of tuples
                              1000, None)
        self.assertRaises(LCRuleTypeError, L2MultipointEndpointLCRule,
                              1,[1,2,3],
                              (4,100), # Must be list of tuples
                              1000, None)
        self.assertRaises(LCRuleTypeError, L2MultipointEndpointLCRule,
                              1,[1,2,3],
                              None, # Must be list of tuples
                              1000, None)

        # intermediate_vlan - must be None or an int.
        self.assertRaises(LCRuleTypeError, L2MultipointEndpointLCRule,
                              1,[1,2,3],[(4,100),(5,200)],
                              [1000], # Must be an int or None
                              None)
        self.assertRaises(LCRuleTypeError, L2MultipointEndpointLCRule,
                              1,[1,2,3],[(4,100),(5,200)],
                              'a', # Must be an int or None
                              None)
        self.assertRaises(LCRuleTypeError, L2MultipointEndpointLCRule,
                              1,[1,2,3],[(4,100),(5,200)],
                              (1,2), # Must be an int or None
                              None)

        # Bandwidth
        self.assertRaises(LCRuleTypeError, L2MultipointEndpointLCRule,
                              1,[1,2,3],[(4,100),(5,200)],1000,
                              1.1) # Must be an int or None
        self.assertRaises(LCRuleTypeError, L2MultipointEndpointLCRule,
                              1,[1,2,3],[(4,100),(5,200)],1000,
                              'a') # Must be an int or None
        self.assertRaises(LCRuleTypeError, L2MultipointEndpointLCRule,
                              1,[1,2,3],[(4,100),(5,200)],1000,
                              (1,2)) # Must be an int or None
        self.assertRaises(LCRuleTypeError, L2MultipointEndpointLCRule,
                              1,[1,2,3],[(4,100),(5,200)],1000,
                              [1,2]) # Must be an int or None

        
                              

if __name__ == '__main__':
    unittest.main()
