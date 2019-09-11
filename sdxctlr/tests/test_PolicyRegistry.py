# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the PolicyRegistry class

import unittest
import threading
#import mock

from sdxctlr.PolicyRegistry import *


class SingletonTest(unittest.TestCase):
    def atest_singleton(self):
        firstRegistry = PolicyRegistry()
        secondRegistry = PolicyRegistry()

        self.failUnless(firstRegistry is secondRegistry)

class AddingPoliciesTest(unittest.TestCase):
    def test_add_policytype(self):
        class FakePolicyType(object):
            def __init__(self):
                self.status = "I am Fake!"
            @classmethod
            def get_policy_name(cls):
                return cls.__name__

        reg = PolicyRegistry()
        reg.add_policytype(FakePolicyType)
        retval = reg.get_policy_class("FakePolicyType")
        self.failUnless(retval is FakePolicyType)


class NonPolicyTest(unittest.TestCase):
    def test_non_policytype(self):
        reg = PolicyRegistry()
        self.failUnlessRaises(PolicyRegistryTypeError,
                              reg.get_policy_class, "TotallyDoesNotExist")
        

class find_policies(unittest.TestCase):
    def test_autopopulate(self):
        reg = PolicyRegistry()
        reg.find_policies()

if __name__ == '__main__':
    unittest.main()
