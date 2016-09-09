# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the RuleManager class

import unittest
import threading
import networkx as nx
#import mock

from sdxctlr.RuleManager import *
from shared.UserPolicy import *
from sdxctlr.TopologyManager import TopologyManager


TOPO_CONFIG_FILE = 'test_manifests/topo.manifest'
class UserPolicyStandin(UserPolicy):
    # Use the username as a return value for checking validity.
    def __init__(self, username, json_rule):
        super(UserPolicyStandin, self).__init__(username, json_rule)
        self.valid = username
        self.breakdown = json_rule
        
    def check_validity(self, topology, authorization_func):
        # Verify that topology is a nx.Graph, and authorization_func is ???
        if not isinstance(topology, nx.Graph):
            raise Exception("Topology is not nx.Graph")
        if self.valid == True:
            return True
        raise Exception("NOT VALID")
    
    def breakdown_rule(self, topology, authorization_func):
        # Verify that topology is a nx.Graph, and authorization_func is ???
        if not isinstance(topology, nx.Graph):
            raise Exception("Topology is not nx.Graph")
        if self.breakdown == True:
            return [UserPolicyBreakdown("1.2.3.4", ["rule1", "rule2"])]
        raise Exception("NO BREAKDOWN")
    
    def _parse_json(self, json_rule):
        return

class SingletonTest(unittest.TestCase):
    def test_singleton(self):
        topo = TopologyManager(TOPO_CONFIG_FILE)
        firstManager = RuleManager()
        secondManager = RuleManager()

        self.failUnless(firstManager is secondManager)

class AddRuleTest(unittest.TestCase):
    def test_good_test_add_rule(self):
        topo = TopologyManager(TOPO_CONFIG_FILE)
        man = RuleManager()
        valid_rule = UserPolicyStandin(True, True)

        #FIXME
        man.test_add_rule(valid_rule)

    def test_invalid_test_add_rule(self):
        topo = TopologyManager(TOPO_CONFIG_FILE)
        man = RuleManager()
        invalid_rule = UserPolicyStandin(False, True)

        self.failUnlessRaises(RuleManagerValidationError,
                              man.test_add_rule, invalid_rule)

    def test_no_breakdown_test_add_rule(self):
        topo = TopologyManager(TOPO_CONFIG_FILE)
        man = RuleManager()
        invalid_rule = UserPolicyStandin(True, False)

        self.failUnlessRaises(RuleManagerBreakdownError,
                              man.test_add_rule, invalid_rule)

    def test_good_add_rule(self):
        topo = TopologyManager(TOPO_CONFIG_FILE)
        man = RuleManager()
        valid_rule = UserPolicyStandin(True, True)

#        print man.add_rule(valid_rule)
        self.failUnless(isinstance(man.add_rule(valid_rule), int))

    def test_invalid_add_rule(self):
        topo = TopologyManager(TOPO_CONFIG_FILE)
        man = RuleManager()
        invalid_rule = UserPolicyStandin(False, True)

        self.failUnlessRaises(RuleManagerValidationError,
                              man.add_rule, invalid_rule)

    def test_no_breakdown_add_rule(self):
        topo = TopologyManager(TOPO_CONFIG_FILE)
        man = RuleManager()
        invalid_rule = UserPolicyStandin(True, False)

        self.failUnlessRaises(RuleManagerBreakdownError,
                              man.add_rule, invalid_rule)

class RemoveRuleTest(unittest.TestCase):
    def test_good_remove_rule(self):
        topo = TopologyManager(TOPO_CONFIG_FILE)
        man = RuleManager()
        valid_rule = UserPolicyStandin(True, True)

        #FIXME
        hash = man.add_rule(valid_rule)
        man.get_rule_details(hash)
        self.failUnless(man.get_rule_details(hash) != None)

        man.remove_rule(hash, "dummy_user")
        self.failUnless(man.get_rule_details(hash) == None)
        
if __name__ == '__main__':
    unittest.main()
