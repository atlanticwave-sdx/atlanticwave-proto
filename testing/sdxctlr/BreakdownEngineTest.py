# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the BreakdownEngine class

import unittest
import threading
import networkx as nx
#import mock

from shared.UserPolicy import UserPolicy
from sdxctlr.BreakdownEngine import *
from sdxctlr.TopologyManager import TopologyManager

TOPO_CONFIG_FILE = 'test_manifests/topo.manifest'
class UserPolicyStandin(UserPolicy):
    # Use the username as a return value 
    def __init__(self, username, json_rule):
        super(UserPolicyStandin, self).__init__(username, json_rule)
        self.retval = username
        
    def breakdown_rule(self, topology, authorization_func):
        # Verify that topology is a nx.Graph, and authorization_func is ???
        if not isinstance(topology, nx.Graph):
            raise Exception("Topology is not nx.Graph")
        if self.retval == True:
            return True
        raise Exception("BAD")
    def _parse_json(self, json_rule):
        return
    

class SingletonTest(unittest.TestCase):
    def test_singleton(self):
        topo = TopologyManager(TOPO_CONFIG_FILE)
        first = BreakdownEngine()
        second =  BreakdownEngine()

        self.failUnless(first is second)

#FIXME: Nothing's mocked here!

class BreakdownTest(unittest.TestCase):
    def test_good_valid(self):
        valid_rule = UserPolicyStandin(True, "")
        topo = TopologyManager(TOPO_CONFIG_FILE)
        engine = BreakdownEngine()
        self.failUnless(engine.get_breakdown(valid_rule))
                        
    def test_bad_valid(self):
        invalid_rule = UserPolicyStandin(False, "")
        topo = TopologyManager(TOPO_CONFIG_FILE)
        engine = BreakdownEngine()
        self.failUnlessRaises(Exception, engine.get_breakdown, invalid_rule)

if __name__ == '__main__':
    unittest.main()
