# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the ValidityInspector class

import unittest
import threading
import networkx as nx
#import mock

from shared.UserPolicy import UserPolicy
from sdxctlr.ValidityInspector import *
from sdxctlr.TopologyManager import TopologyManager

TOPO_CONFIG_FILE = 'sdxctlr/tests/test_manifests/topo.manifest'
class UserPolicyStandin(UserPolicy):
    # Use the username as a return value for checking validity.
    def __init__(self, username, json_policy):
        super(UserPolicyStandin, self).__init__(username, json_policy)
        self.retval = username
        
    def check_validity(self, topology, authorization_func):
        # Verify that topology is a nx.Graph, and authorization_func is ???
        if not isinstance(topology, nx.Graph):
            raise Exception("Topology is not nx.Graph (%s)" % topology)
        if self.retval == True:
            return True
        raise Exception("BAD")
    def _parse_json(self, json_policy):
        return
    

class SingletonTest(unittest.TestCase):
    def test_singleton(self):
        topo = TopologyManager(topology_file=TOPO_CONFIG_FILE)
        firstInspector = ValidityInspector()
        secondInspector = ValidityInspector()

        self.failUnless(firstInspector is secondInspector)

#FIXME: Nothing's mocked here!

class ValidityTest(unittest.TestCase):
    def test_good_valid(self):
        valid_policy = UserPolicyStandin(True, "")
        inspector = ValidityInspector()
        self.failUnless(inspector.is_valid_policy(valid_policy))
                        
    def test_bad_valid(self):
        invalid_policy = UserPolicyStandin(False, "")
        inspector = ValidityInspector()
        self.failUnlessRaises(Exception, inspector.is_valid_policy,
                              invalid_policy)

if __name__ == '__main__':
    unittest.main()
