from __future__ import unicode_literals
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

TOPO_CONFIG_FILE = 'tests/test_manifests/topo.manifest'
class UserPolicyStandin(UserPolicy):
    # Use the username as a return value for checking validity.
    def __init__(self, username, json_rule):
        super(UserPolicyStandin, self).__init__(username, json_rule)
        self.retval = username
        
    def check_validity(self, topology, authorization_func):
        # Verify that topology is a nx.Graph, and authorization_func is ???
        if not isinstance(topology, nx.Graph):
            raise Exception("Topology is not nx.Graph (%s)" % topology)
        if self.retval == True:
            return True
        raise Exception("BAD")
    def _parse_json(self, json_rule):
        return
    

class SingletonTest(unittest.TestCase):
    def test_singleton(self):
        topo = TopologyManager(topology_file=TOPO_CONFIG_FILE)
        firstInspector = ValidityInspector()
        secondInspector = ValidityInspector()

        self.assert(firstInspector is secondInspector)

#FIXME: Nothing's mocked here!

class ValidityTest(unittest.TestCase):
    def test_good_valid(self):
        valid_rule = UserPolicyStandin(True, "")
        inspector = ValidityInspector()
        self.assert(inspector.is_valid_rule(valid_rule))
                        
    def test_bad_valid(self):
        invalid_rule = UserPolicyStandin(False, "")
        inspector = ValidityInspector()
        self.assertRaises(Exception, inspector.is_valid_rule, invalid_rule)

if __name__ == '__main__':
    unittest.main()
