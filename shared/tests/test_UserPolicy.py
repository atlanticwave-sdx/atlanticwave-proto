from __future__ import unicode_literals
# Copyright 2019 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for shared.UserPolicy module

import unittest
import mock
from shared.UserPolicy import *
from shared.LCRule import *

class BasicTest(unittest.TestCase):
    # UserPolicy is meant to be subclassed, so there's a whole mess of
    # NotImplementedErrors scattered about. Mock is going to be heavily used.
    
    def test_init_catch_error(self):
        self.assertRaises(NotImplementedError,
                              UserPolicy,
                              'sdonovan',
                              'teststring')

    @mock.patch('shared.UserPolicy.UserPolicy._parse_json', autospec=True)
    def test_init(self, uppatch):
        up = UserPolicy('sdonovan', 'teststring')

        self.assertRaises(NotImplementedError,
                              up.breakdown_rule,
                              None,
                              None)
        self.assertRaises(NotImplementedError,
                              up.check_validity,
                              None,
                              None)
        # These shouldn't break or do anything
        up.pre_add_callback(None, None) 
        up.pre_remove_callback(None, None)
        up.switch_change_callback(None, None, None)

    @mock.patch('shared.UserPolicy.UserPolicy._parse_json', autospec=True)
    def test_get_fcns(self, uppatch):
        up = UserPolicy('sdonovan', 'teststring')

        # The gets default usually to None or []. Some are passed in at the
        # beginning and some are (predictably) generated.
        self.assertEquals([], up.get_endpoints())
        self.assertEquals(None, up.get_bandwidth())
        self.assertEquals(None, up.get_breakdown())
        self.assertEquals(None, up.get_start_time())
        self.assertEquals(None, up.get_stop_time())
        self.assertEquals('teststring', up.get_json_rule()) # passed in
        self.assertEquals('User', up.get_ruletype()) # Generated
        self.assertEquals('sdonovan', up.get_user()) # passed in
        self.assertEquals(None, up.get_rule_hash())
        self.assertEquals([], up.get_resources())
        

    @mock.patch('shared.UserPolicy.UserPolicy._parse_json', autospec=True)
    def test_set_fcns(self, uppatch):
        up = UserPolicy('sdonovan', 'teststring')

        # The gets default usually to None or []. Some are passed in at the
        # beginning and some are (predictably) generated.
        self.assertEquals(None, up.get_breakdown())
        self.assertEquals('teststring', up.get_json_rule()) # passed in
        self.assertEquals('User', up.get_ruletype()) # Generated
        self.assertEquals('sdonovan', up.get_user()) # passed in
        self.assertEquals(None, up.get_rule_hash())

        up.set_breakdown("testbreakdown")
        self.assertEquals("testbreakdown", up.get_breakdown())

        up.set_rule_hash(12345)
        self.assertEquals(12345, up.get_rule_hash())

class ClassMethodsTest(unittest.TestCase):
    # There are a couple of ClassMethods we need to test.

    def setUp(self):
        self.filecontents = mock.mock_open(read_data =
                                           ("firstline\nsecondline\n"
                                            "thirdline\nforthline\n"))
    def test_not_implemented_class_methods(self):
        self.assertRaises(NotImplementedError,
                              UserPolicy.check_syntax,
                              "TestJson")

    @mock.patch('shared.UserPolicy.UserPolicy._parse_json', autospec=True)
    def test_get_html_help(self, uppatch):
        with mock.patch('__builtin__.open', self.filecontents):
            self.assertEquals("firstline\nsecondline\nthirdline\nforthline\n",
                              UserPolicy.get_html_help())
    
    def test_get_policy_name(self):
        self.assertEquals("User", UserPolicy.get_policy_name())
        


class BasicBreakdownTest(unittest.TestCase):
    def test_init(self):
        bd1 = UserPolicyBreakdown('LC', ['a','b'])
        self.assertEquals(bd1.get_lc(), 'LC')
        self.assertEquals(bd1.get_list_of_rules(), ['a','b'])

        bd2 = UserPolicyBreakdown('LC2', [])
        self.assertEquals(bd2.get_lc(), 'LC2')
        self.assertEquals(bd2.get_list_of_rules(), [])

    def test_add(self):
        bd = UserPolicyBreakdown('LC', ['a','b'])
        self.assertEquals(bd.get_lc(), 'LC')
        self.assertEquals(bd.get_list_of_rules(), ['a','b'])
        bd.add_to_list_of_rules('c')
        self.assertEquals(bd.get_list_of_rules(), ['a','b','c'])

    def test_set_cookie(self):
        list_of_rules = [LCRule(1),
                         LCRule(2)]
        list_of_rules_with_cookies = [LCRule(1,'cookie'),
                                      LCRule(2,'cookie')]

        bd = UserPolicyBreakdown('LC', list_of_rules)
        self.assertEquals(bd.get_lc(), 'LC')
        self.assertEquals(bd.get_list_of_rules(), list_of_rules)

        bd.set_cookie("cookie")
        self.assertEquals(bd.get_lc(), 'LC')
        self.assertEquals(bd.get_list_of_rules(), list_of_rules_with_cookies)
        
        

if __name__ == '__main__':
    unittest.main()
