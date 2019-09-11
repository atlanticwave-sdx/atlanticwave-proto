# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the RuleRegistry class

import unittest
import threading
#import mock

from sdxctlr.RuleRegistry import *


class SingletonTest(unittest.TestCase):
    def atest_singleton(self):
        firstRegistry = RuleRegistry()
        secondRegistry = RuleRegistry()

        self.failUnless(firstRegistry is secondRegistry)

class AddingRulesTest(unittest.TestCase):
    def atest_add_ruletype(self):
        class FakeRuleType(object):
            def __init__(self):
                self.status = "I am Fake!"
            @classmethod
            def get_policy_name(cls):
                return cls.__name__

        reg = RuleRegistry()
        reg.add_ruletype(FakeRuleType)
        retval = reg.get_rule_class("FakeRuleType")
        self.failUnless(retval is FakeRuleType)


class NonRuleTest(unittest.TestCase):
    def atest_non_ruletype(self):
        reg = RuleRegistry()
        self.failUnlessRaises(RuleRegistryTypeError,
                              reg.get_rule_class, "TotallyDoesNotExist")
        

class find_policies(unittest.TestCase):
    def test_autopopulate(self):
        reg = RuleRegistry()
        reg.find_policies("../../shared/")

if __name__ == '__main__':
    unittest.main()
