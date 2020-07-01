from __future__ import unicode_literals
# Copyright 2019 - Sean Donovan
# AlanticWave/SDX Project


# Unit tests for shared.L2MultipointEndpointLCRule

from builtins import str
import unittest
from shared.PathResource import *

class BasicPathResourceTest(unittest.TestCase):
    def test_basic_resource(self):
        pr1 = PathResource('a','b','c')

        self.assertEqual('a', pr1._name)
        self.assertEqual('b', pr1.get_location())
        self.assertEqual('c', pr1.get_value())
        self.assertEqual("a: b,c", str(pr1))

    def test_equality(self):
        pr1 = PathResource('a','b','c')
        pr2 = PathResource('a','b','c')
        pr3 = PathResource('x','b','c')
        pr4 = PathResource('a','x','c')
        pr5 = PathResource('a','b','x')

        self.assertEqual(pr1, pr2)
        self.assertNotEqual(pr1, pr3)
        self.assertNotEqual(pr1, pr4)
        self.assertNotEqual(pr1, pr5)

class BasicVLANPortResourceTest(unittest.TestCase):
    def test_basic_resource(self):
        pr1 = VLANPortResource(1,2,1000)

        self.assertEqual('VLAN Port', pr1._name)
        self.assertEqual((1,2), pr1.get_location())
        self.assertEqual(1000, pr1.get_value())

        self.assertEqual(1, pr1.get_switch())
        self.assertEqual(2, pr1.get_port())
        self.assertEqual(1000, pr1.get_vlan())                   
        self.assertEqual("VLAN Port: (1, 2),1000", str(pr1))

    def test_equality(self):
        pr1 = VLANPortResource(1,2,1000)
        pr2 = VLANPortResource(1,2,1000)
        pr3 = VLANPortResource(9,2,1000)
        pr4 = VLANPortResource(1,9,1000)
        pr5 = VLANPortResource(1,2,9)

        self.assertEqual(pr1, pr2)
        self.assertNotEqual(pr1, pr3)
        self.assertNotEqual(pr1, pr4)
        self.assertNotEqual(pr1, pr5)

class BasicVLANPathResourceTest(unittest.TestCase):
    def test_basic_resource(self):
        pr1 = VLANPathResource([1,2],1000)

        self.assertEqual('VLAN Path', pr1._name)
        self.assertEqual([1,2], pr1.get_location())
        self.assertEqual(1000, pr1.get_value())

        self.assertEqual([1,2], pr1.get_path())
        self.assertEqual(1000, pr1.get_vlan())                   
        self.assertEqual("VLAN Path: [1, 2],1000", str(pr1))

    def test_equality(self):
        pr1 = VLANPathResource([1,2],1000)
        pr2 = VLANPathResource([1,2],1000)
        pr3 = VLANPathResource([1,9],1000)
        pr4 = VLANPathResource([1,2,9],1000)
        pr5 = VLANPathResource([1,2],10000)

        self.assertEqual(pr1, pr2)
        self.assertNotEqual(pr1, pr3)
        self.assertNotEqual(pr1, pr4)
        self.assertNotEqual(pr1, pr5)
    
class BasicVLANTreeResourceTest(unittest.TestCase):
    def test_basic_resource(self):
        pr1 = VLANTreeResource([1,2],1000)

        self.assertEqual('VLAN Tree', pr1._name)
        self.assertEqual([1,2], pr1.get_location())
        self.assertEqual(1000, pr1.get_value())

        self.assertEqual([1,2], pr1.get_tree())
        self.assertEqual(1000, pr1.get_vlan())                   
        self.assertEqual("VLAN Tree: [1, 2],1000", str(pr1))

    def test_equality(self):
        pr1 = VLANTreeResource([1,2],1000)
        pr2 = VLANTreeResource([1,2],1000)
        pr3 = VLANTreeResource([1,9],1000)
        pr4 = VLANTreeResource([1,2,9],1000)
        pr5 = VLANTreeResource([1,2],10000)

        self.assertEqual(pr1, pr2)
        self.assertNotEqual(pr1, pr3)
        self.assertNotEqual(pr1, pr4)
        self.assertNotEqual(pr1, pr5)                              

class BasicBandwidthPathResourceTest(unittest.TestCase):
    def test_basic_resource(self):
        pr1 = BandwidthPathResource([1,2],1000)

        self.assertEqual('B/W Path', pr1._name)
        self.assertEqual([1,2], pr1.get_location())
        self.assertEqual(1000, pr1.get_value())

        self.assertEqual([1,2], pr1.get_path())
        self.assertEqual(1000, pr1.get_bandwidth())                   
        self.assertEqual("B/W Path: [1, 2],1000", str(pr1))

    def test_equality(self):
        pr1 = BandwidthPathResource([1,2],1000)
        pr2 = BandwidthPathResource([1,2],1000)
        pr3 = BandwidthPathResource([1,9],1000)
        pr4 = BandwidthPathResource([1,2,9],1000)
        pr5 = BandwidthPathResource([1,2],10000)

        self.assertEqual(pr1, pr2)
        self.assertNotEqual(pr1, pr3)
        self.assertNotEqual(pr1, pr4)
        self.assertNotEqual(pr1, pr5)
    
class BasicBandwidthTreeResourceTest(unittest.TestCase):
    def test_basic_resource(self):
        pr1 = BandwidthTreeResource([1,2],1000)

        self.assertEqual('B/W Tree', pr1._name)
        self.assertEqual([1,2], pr1.get_location())
        self.assertEqual(1000, pr1.get_value())

        self.assertEqual([1,2], pr1.get_tree())
        self.assertEqual(1000, pr1.get_bandwidth())                   
        self.assertEqual("B/W Tree: [1, 2],1000", str(pr1))

    def test_equality(self):
        pr1 = BandwidthTreeResource([1,2],1000)
        pr2 = BandwidthTreeResource([1,2],1000)
        pr3 = BandwidthTreeResource([1,9],1000)
        pr4 = BandwidthTreeResource([1,2,9],1000)
        pr5 = BandwidthTreeResource([1,2],10000)

        self.assertEqual(pr1, pr2)
        self.assertNotEqual(pr1, pr3)
        self.assertNotEqual(pr1, pr4)
        self.assertNotEqual(pr1, pr5)           
if __name__ == '__main__':
    unittest.main()
