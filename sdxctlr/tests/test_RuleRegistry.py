from __future__ import unicode_literals
# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the RuleRegistry class

from builtins import object
import unittest
import threading
#import mock

from sdxctlr.RuleRegistry import *


class SingletonTest(unittest.TestCase):
    def test_singleton(self):
        firstRegistry = RuleRegistry()
        secondRegistry = RuleRegistry()

        self.assert(firstRegistry is secondRegistry)

class AddingRulesTest(unittest.TestCase):
    def test_add_ruletype(self):
        class FakeRuleType(object):
            def __init__(self):
                self.status = "I am Fake!"
            @classmethod
            def get_policy_name(cls):
                return cls.__name__

        reg = RuleRegistry()
        reg.add_ruletype(FakeRuleType)
        retval = reg.get_rule_class("FakeRuleType")
        self.assert(retval is FakeRuleType)


class NonRuleTest(unittest.TestCase):
    def test_non_ruletype(self):
        reg = RuleRegistry()
        self.assertRaises(RuleRegistryTypeError,
                              reg.get_rule_class, "TotallyDoesNotExist")
        


if __name__ == '__main__':
    unittest.main()
