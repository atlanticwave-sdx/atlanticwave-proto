# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for shared.offield module

import unittest
from shared.LCFields import *


class BasicFieldTest(unittest.TestCase):
    def test_basic_init(self):
        a_field = LCField('field')
        return

    def test_empty_init(self):
        try:
            a_field = LCField()
        except TypeError:
            pass
        else:
            self.fail("did not see error")

    def test_equality(self):
        a_field = LCField('field')
        b_field = LCField('field')
        self.failUnlessEqual(a_field, b_field)

        c_field = LCField('field', 1)
        d_field = LCField('field', 1)
        self.failUnlessEqual(c_field, d_field)

    def test_get(self):
        a_field = LCField('field', 1)
        self.failUnlessEqual(a_field.get(), 1)

        b_field = LCField('field')
        self.failUnlessEqual(b_field.get(), None)
        
    def test_set(self):
        a_field = LCField('field')
        b_field = LCField('field')
        self.failUnlessEqual(a_field, b_field)

        a_field.set(3)
        b_field.set(3)
        self.failUnlessEqual(a_field, b_field)
        self.failUnlessEqual(a_field.get(), 3)
        self.failUnlessEqual(a_field.get(), 3)
        

    def test_validity(self):
        try:
            a_field = LCField('field')
            a_field.check_validity()
        except NotImplementedError:
            pass
        else:
            self.fail("did not see error")

        
        
class NumberFieldTest(unittest.TestCase):
    def test_basic_init(self):
        num_field = number_field('field', 1, 100)
        num_field2 = number_field('field', 1, 100, others=[102])
        num_field3 = number_field('field', 1, 100, others=[102,103])

        self.failUnlessRaises(TypeError, number_field, 'field', 1, 100, value="a")
    
    def test_empty_init(self):
        try:
            num_field = number_field('field')
        except TypeError:
            pass
        else:
            self.fail("did not see error")
            
    def test_empty_init2(self):
        try:
            num_field = number_field('field', 1)
        except TypeError:
            pass
        else:
            self.fail("did not see error")

    def test_validity_pass(self):
        num_field1 = number_field('field', 1, 100, value=50)
        num_field2 = number_field('field', 1, 100, value=1)
        num_field3 = number_field('field', 1, 100, value=100)
        num_field4 = number_field('field', 1, 100, others=[105], value=105)

        num_field1.check_validity()
        num_field2.check_validity()
        num_field3.check_validity()
        num_field4.check_validity()

    def test_validity(self):
        num_field = number_field('field', 1, 100, value=103)
        num_field2 = number_field('field', 1, 100, others=[102], value=103)
        num_field3 = number_field('field', 1, 100, others=[102,103], value=103)
        num_field4 = number_field('field', 1, 100)

        num_field4.set("a")

#        print num_field.__repr__()
#        print num_field
#        print num_field2.__repr__()
#        print num_field2
#        print num_field3.__repr__()
#        print num_field3
#        print num_field4.__repr__()
#        print num_field4
        

        self.failUnlessRaises(TypeError, num_field4.check_validity)
        self.failUnlessRaises(ValueError, num_field.check_validity)
        self.failUnlessRaises(ValueError, num_field2.check_validity)
        num_field3.check_validity()
    

#TODO - class BitmaskFieldTest(

#TODO - class IPv4FieldTest(unittest.TestCase):

#TODO - class IPv6FieldTest(unittest.TestCase):





        
if __name__ == '__main__':
    unittest.main()
