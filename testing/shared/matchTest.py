# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import unittest
from shared.match import *
from shared.offield import *

class BasicOpenFlowMatchTest(unittest.TestCase):
    def test_basic_init(self):
        fields = [Field('field')]
        match = OpenFlowMatch(fields)

    def test_empty_init(self):
        try:
            match = OpenFlowMatch()
        except TypeError:
            pass
        else:
            self.fail("did not see error")

    def test_invalid_init1(self):
        fields = Field('field')
        try:
            match = OpenFlowMatch(fields)
        except TypeError:
            pass
        else:
            self.fail("did not see error")

            
    def test_invalid_init2(self):
        fields = ['a', 'b', 'c']
        try:
            match = OpenFlowMatch(fields)
        except TypeError:
            pass
        else:
            self.fail("did not see error")
            
    def test_invalid_init3(self):
        # incorrect fields type
        fields = [Field('field'), 'b', 'c']
        try:
            match = OpenFlowMatch(fields)
        except TypeError:
            pass
        else:
            self.fail("did not see error")

    def test_check_validity_valid(self):
        # Stolen from actionTest.py
        # Borrowing from offieldtest.py BasicFieldTest.test_is_optional
        required_field = number_field('required', 0, 100, value=1)
        notrequired_field = number_field('notrequired', 0, 100, value=0)
        optional_field = number_field('opt', 0, 100, value=1, prereq=[number_field('required', 0, 100, value=1)])
        all_fields = [required_field, notrequired_field, optional_field]

        # These should pass
        OpenFlowMatch([]).check_validity()
        OpenFlowMatch([required_field]).check_validity()
        OpenFlowMatch([notrequired_field]).check_validity()
        OpenFlowMatch([required_field, notrequired_field]).check_validity()
        OpenFlowMatch([required_field, optional_field]).check_validity()
        OpenFlowMatch(all_fields).check_validity()
        print OpenFlowMatch(all_fields).__repr__()
        print OpenFlowMatch(all_fields)
        
    def test_check_validity_invalid(self):
        # Stolen from actionTest.py
        # Borrowing from offieldtest.py BasicFieldTest.test_is_optional
        required_field = number_field('required', 0, 100, value=1)
        notrequired_field = number_field('notrequired', 0, 100, value=0)
        optional_field = number_field('opt', 0, 100, value=1, prereq=[number_field('required', 0, 100, value=1)])
        all_fields = [required_field, notrequired_field, optional_field]        

        try:
            OpenFlowMatch([optional_field]).check_validity()
        except ValueError:
            pass
        else:
            self.fail("did not see error")

    def test_check_prerequisites_valid(self):
        # Stolen from actionTest.py
        # Borrowing from offieldtest.py BasicFieldTest.test_is_optional
        required_field = number_field('required', 0, 100, value=1)
        notrequired_field = number_field('notrequired', 0, 100, value=0)
        optional_field = number_field('opt', 0, 100, value=1, prereq=[number_field('required', 0, 100, value=1)])
        all_fields = [required_field, notrequired_field, optional_field]        

        try:
            OpenFlowMatch([optional_field]).check_validity()
        except ValueError:
            pass
        else:
            self.fail("did not see error")

    def test_check_prerequisites_invalid(self):
        # Stolen from actionTest.py
        # Borrowing from offieldtest.py BasicFieldTest.test_is_optional
        required_field = number_field('required', 0, 100, value=1)
        notrequired_field = number_field('notrequired', 0, 100, value=0)
        optional_field = number_field('opt', 0, 100, value=1, prereq=[number_field('required', 0, 100, value=1)])
        all_fields = [required_field, notrequired_field, optional_field]        

        try:
            OpenFlowMatch([notrequired_field, optional_field]).check_validity()
        except ValueError:
            pass
        else:
            self.fail("did not see error")






       
if __name__ == '__main__':
    unittest.main()
