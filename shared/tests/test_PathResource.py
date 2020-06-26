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

        self.assertEquals('a', pr1._name)
        self.assertEquals('b', pr1.get_location())
        self.assertEquals('c', pr1.get_value())
        self.assertEquals("a: b,c", str(pr1))

    def test_equality(self):
        pr1 = PathResource('a','b','c')
        pr2 = PathResource('a','b','c')
        pr3 = PathResource('x','b','c')
        pr4 = PathResource('a','x','c')
        pr5 = PathResource('a','b','x')

        self.assertEquals(pr1, pr2)
        self.assertNotEquals(pr1, pr3)
        self.assertNotEquals(pr1, pr4)
        self.assertNotEquals(pr1, pr5)

class BasicVLANPortResourceTest(unittest.TestCase):
    def test_basic_resource(self):
        pr1 = VLANPortResource(1,2,1000)

        self.assertEquals('VLAN Port', pr1._name)
        self.assertEquals((1,2), pr1.get_location())
        self.assertEquals(1000, pr1.get_value())

        self.assertEquals(1, pr1.get_switch())
        self.assertEquals(2, pr1.get_port())
        self.assertEquals(1000, pr1.get_vlan())                   
        self.assertEquals("VLAN Port: (1, 2),1000", str(pr1))

    def test_equality(self):
        pr1 = VLANPortResource(1,2,1000)
        pr2 = VLANPortResource(1,2,1000)
        pr3 = VLANPortResource(9,2,1000)
        pr4 = VLANPortResource(1,9,1000)
        pr5 = VLANPortResource(1,2,9)

        self.assertEquals(pr1, pr2)
        self.assertNotEquals(pr1, pr3)
        self.assertNotEquals(pr1, pr4)
        self.assertNotEquals(pr1, pr5)

class BasicVLANPathResourceTest(unittest.TestCase):
    def test_basic_resource(self):
        pr1 = VLANPathResource([1,2],1000)

        self.assertEquals('VLAN Path', pr1._name)
        self.assertEquals([1,2], pr1.get_location())
        self.assertEquals(1000, pr1.get_value())

        self.assertEquals([1,2], pr1.get_path())
        self.assertEquals(1000, pr1.get_vlan())                   
        self.assertEquals("VLAN Path: [1, 2],1000", str(pr1))

    def test_equality(self):
        pr1 = VLANPathResource([1,2],1000)
        pr2 = VLANPathResource([1,2],1000)
        pr3 = VLANPathResource([1,9],1000)
        pr4 = VLANPathResource([1,2,9],1000)
        pr5 = VLANPathResource([1,2],1000)

        self.assertEquals(pr1, pr2)
        self.assertNotEquals(pr1, pr3)
        self.assertNotEquals(pr1, pr4)
        self.assertNotEquals(pr1, pr5)
    
class BasicVLANTreeResourceTest(unittest.TestCase):
    def test_basic_resource(self):
        pr1 = VLANTreeResource([1,2],1000)

        self.assertEquals('VLAN Tree', pr1._name)
        self.assertEquals([1,2], pr1.get_location())
        self.assertEquals(1000, pr1.get_value())

        self.assertEquals([1,2], pr1.get_tree())
        self.assertEquals(1000, pr1.get_vlan())                   
        self.assertEquals("VLAN Tree: [1, 2],1000", str(pr1))

    def test_equality(self):
        pr1 = VLANTreeResource([1,2],1000)
        pr2 = VLANTreeResource([1,2],1000)
        pr3 = VLANTreeResource([1,9],1000)
        pr4 = VLANTreeResource([1,2,9],1000)
        pr5 = VLANTreeResource([1,2],1000)

        self.assertEquals(pr1, pr2)
        self.assertNotEquals(pr1, pr3)
        self.assertNotEquals(pr1, pr4)
        self.assertNotEquals(pr1, pr5)                              

class BasicBandwidthPathResourceTest(unittest.TestCase):
    def test_basic_resource(self):
        pr1 = BandwidthPathResource([1,2],1000)

        self.assertEquals('B/W Path', pr1._name)
        self.assertEquals([1,2], pr1.get_location())
        self.assertEquals(1000, pr1.get_value())

        self.assertEquals([1,2], pr1.get_path())
        self.assertEquals(1000, pr1.get_bandwidth())                   
        self.assertEquals("B/W Path: [1, 2],1000", str(pr1))

    def test_equality(self):
        pr1 = BandwidthPathResource([1,2],1000)
        pr2 = BandwidthPathResource([1,2],1000)
        pr3 = BandwidthPathResource([1,9],1000)
        pr4 = BandwidthPathResource([1,2,9],1000)
        pr5 = BandwidthPathResource([1,2],1000)

        self.assertEquals(pr1, pr2)
        self.assertNotEquals(pr1, pr3)
        self.assertNotEquals(pr1, pr4)
        self.assertNotEquals(pr1, pr5)
    
class BasicBandwidthTreeResourceTest(unittest.TestCase):
    def test_basic_resource(self):
        pr1 = BandwidthTreeResource([1,2],1000)

        self.assertEquals('B/W Tree', pr1._name)
        self.assertEquals([1,2], pr1.get_location())
        self.assertEquals(1000, pr1.get_value())

        self.assertEquals([1,2], pr1.get_tree())
        self.assertEquals(1000, pr1.get_bandwidth())                   
        self.assertEquals("B/W Tree: [1, 2],1000", str(pr1))

    def test_equality(self):
        pr1 = BandwidthTreeResource([1,2],1000)
        pr2 = BandwidthTreeResource([1,2],1000)
        pr3 = BandwidthTreeResource([1,9],1000)
        pr4 = BandwidthTreeResource([1,2,9],1000)
        pr5 = BandwidthTreeResource([1,2],1000)

        self.assertEquals(pr1, pr2)
        self.assertNotEquals(pr1, pr3)
        self.assertNotEquals(pr1, pr4)
        self.assertNotEquals(pr1, pr5)           
if __name__ == '__main__':
    unittest.main()
