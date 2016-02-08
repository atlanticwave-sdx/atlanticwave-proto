# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for shared.offield module

import unittest
from shared.offield import *


class BasicFieldTest(unittest.TestCase):
    def test_basic_init(self):
        a_field = Field('field')
        return

    def test_empty_init(self):
        try:
            a_field = Field()
        except TypeError:
            pass
        else:
            self.fail("did not see error")

    def test_equality(self):
        a_field = Field('field')
        b_field = Field('field')
        self.failUnlessEqual(a_field, b_field)

        c_field = Field('field', 1)
        d_field = Field('field', 1)
        self.failUnlessEqual(c_field, d_field)

    def test_get(self):
        a_field = Field('field', 1)
        self.failUnlessEqual(a_field.get(), 1)

        b_field = Field('field')
        self.failUnlessEqual(b_field.get(), None)
        
    def test_set(self):
        a_field = Field('field')
        b_field = Field('field')
        self.failUnlessEqual(a_field, b_field)

        a_field.set(3)
        b_field.set(3)
        self.failUnlessEqual(a_field, b_field)
        self.failUnlessEqual(a_field.get(), 3)
        self.failUnlessEqual(a_field.get(), 3)
        

    def test_validity(self):
        try:
            a_field = Field('field')
            a_field.check_validity()
        except NotImplementedError:
            pass
        else:
            self.fail("did not see error")

    def test_is_optional(self):
        required_field = Field('required', 1)
        notrequired_field = Field('required', 0)
        optional_field = Field('opt', 1, optional_without=Field('required', 1))

        self.failUnlessEqual(True, optional_field.is_optional([]))
        self.failUnlessEqual(True, optional_field.is_optional([notrequired_field]))
        self.failUnlessEqual(False, optional_field.is_optional([required_field]))
        self.failUnlessEqual(False, optional_field.is_optional([notrequired_field,
                                                                required_field]))
        
    def check_prerequisites(self):
        required_field = Field('required', 1)
        notrequired_field = Field('required', 0)
        optional_field = Field('opt', 1, prereq=Field('required', 1))

        required_field.check_prerequisites([])
        required_field.check_prerequisites([notrequired_field])
        required_field.check_prerequisites([required_field,
                                            notrequired_field])
        required_field.check_prerequisites([required_field,
                                            notrequired_field,
                                            optional_field])
        notrequired_field.check_prerequisites([])
        notrequired_field.check_prerequisites([notrequired_field])
        notrequired_field.check_prerequisites([required_field,
                                               notrequired_field])
        notrequired_field.check_prerequisites([required_field,
                                               notrequired_field,
                                               optional_field])
        self.failUnlessRaises(ValueError, optional_field.check_prerequisites)
        self.failUnlessRaises(ValueError, optional_field.check_prerequisites,
                              [notrequired_field])
        optional_field.check_prerequisites([required_field,
                                            notrequired_field])
        optional_field.check_prerequisites([required_field,
                                            notrequired_field,
                                            optional_field])

        
        
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

        self.failUnlessRaises(TypeError, num_field4.check_validity)
        self.failUnlessRaises(ValueError, num_field.check_validity)
        self.failUnlessRaises(ValueError, num_field2.check_validity)
        num_field3.check_validity()
    

#TODO - class BitmaskFieldTest(

#TODO - class IPv4FieldTest(unittest.TestCase):

#TODO - class IPv6FieldTest(unittest.TestCase):








        
if __name__ == '__main__':
    unittest.main()
