# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for shared.action module

import unittest
from shared.action import *

# This should be run after offieldTest.py

class BasicActionTest(unittest.TestCase):
    def test_basic_init(self):
        fields = [Field('field'), Field('field')]
        action = OpenFlowAction(fields)

    def test_empty_init(self):
        try:
            action = OpenFlowAction()
        except TypeError:
            pass
        else:
            self.fail("did not see error")
        
    def test_invalid_init1(self):
        # incorrect fields type
        fields = Field('field')
        try:
            action = OpenFlowAction(fields)
        except TypeError:
            pass
        else:
            self.fail("did not see error")

    def test_invalid_init2(self):
        # incorrect fields type
        fields = ['a', 'b', 'c']
        try:
            action = OpenFlowAction(fields)
        except TypeError:
            pass
        else:
            self.fail("did not see error")

    def test_invalid_init3(self):
        # incorrect fields type
        fields = [Field('field'), 'b', 'c']
        try:
            action = OpenFlowAction(fields)
        except TypeError:
            pass
        else:
            self.fail("did not see error")

    def test_check_validity_valid(self):
        # Borrowing from offieldtest.py BasicFieldTest.test_is_optional
        required_field = number_field('required', 0, 100, value=1)
        notrequired_field = number_field('notrequired', 0, 100, value=0)
        optional_field = number_field('opt', 0, 100, value=1, prereq=[number_field('required', 0, 100, value=1)])
        all_fields = [required_field, notrequired_field, optional_field]

        # These should pass
        OpenFlowAction([]).check_validity()
        OpenFlowAction([required_field]).check_validity()
        OpenFlowAction([notrequired_field]).check_validity()
        OpenFlowAction([required_field, notrequired_field]).check_validity()
        OpenFlowAction([required_field, optional_field]).check_validity()
        OpenFlowAction(all_fields).check_validity()

    def test_check_validity_failure1(self):
        # Borrowing from offieldtest.py BasicFieldTest.test_is_optional
        required_field = number_field('required', 0, 100, value=1)
        notrequired_field = number_field('notrequired', 0, 100, value=0)
        optional_field = number_field('opt', 0, 100, value=1, prereq=[number_field('required', 0, 100, value=1)])
        all_fields = [required_field, notrequired_field, optional_field]        

        try:
            OpenFlowAction([optional_field]).check_validity()
        except ValueError:
            pass
        else:
            self.fail("did not see error")

    def test_check_validity_failure2(self):
        # Borrowing from offieldtest.py BasicFieldTest.test_is_optional
        required_field = number_field('required', 0, 100, value=1)
        notrequired_field = number_field('notrequired', 0, 100, value=0)
        optional_field = number_field('opt', 0, 100, value=1, prereq=[number_field('required', 0, 100, value=1)])
        all_fields = [required_field, notrequired_field, optional_field]        

        try:
            OpenFlowAction([notrequired_field, optional_field]).check_validity()
        except ValueError:
            pass
        else:
            self.fail("did not see error")

        


class action_OUTPUTTest(unittest.TestCase):
    pass

class action_SET_FIELDTest(unittest.TestCase):
    pass






        
if __name__ == '__main__':
    unittest.main()
