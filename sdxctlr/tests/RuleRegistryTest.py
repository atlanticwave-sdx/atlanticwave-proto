# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the RuleRegistry class

import unittest
import threading
#import mock

from sdxctlr.RuleRegistry import *


class SingletonTest(unittest.TestCase):
    def test_singleton(self):
        firstRegistry = RuleRegistry()
        secondRegistry = RuleRegistry()

        self.failUnless(firstRegistry is secondRegistry)

class AddingRulesTest(unittest.TestCase):
    def test_add_ruletype(self):
        class FakeRuleType(object):
            def __init__(self):
                self.status = "I am Fake!"

        reg = RuleRegistry()
        reg.add_ruletype("fakerule", FakeRuleType)
        retval = reg.get_rule_class("fakerule")
        self.failUnless(retval is FakeRuleType)


class NonRuleTest(unittest.TestCase):
    def test_non_ruletype(self):
        reg = RuleRegistry()
        self.failUnlessRaises(RuleRegistryTypeError,
                              reg.get_rule_class, "TotallyDoesNotExist")
        


if __name__ == '__main__':
    unittest.main()
