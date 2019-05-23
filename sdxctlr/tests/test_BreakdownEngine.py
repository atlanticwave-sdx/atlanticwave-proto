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
        print "retval = %s" % self.retval
        
    def breakdown_rule(self, topology, authorization_func):
        # Verify that topology is a nx.Graph, and authorization_func is ???
        print "breakdown_rule called: %s:%s" % (authorization_func, topology)
        if not isinstance(topology, TopologyManager):
            print "- Raising Exception"
            raise Exception("Topology is not nx.Graph")
        if self.retval == True:
            print "- Success"
            return "Success"
        raise Exception("BAD")
    def _parse_json(self, json_rule):
        return
    

class SingletonTest(unittest.TestCase):
    def test_singleton(self):
        print "&&& TEST_SINGLETON &&&"
        topo = TopologyManager(topology_file=TOPO_CONFIG_FILE)
        first = BreakdownEngine()
        second =  BreakdownEngine()

        self.failUnless(first is second)
        del topo

#FIXME: Nothing's mocked here!

class BreakdownTest(unittest.TestCase):
    def test_good_valid(self):
        print "&&& GOOD &&&"
        valid_rule = UserPolicyStandin(True, "")
        topo = TopologyManager(topology_file=TOPO_CONFIG_FILE)
        engine = BreakdownEngine()
        self.assertEquals(engine.get_breakdown(valid_rule), "Success")
        del topo
                        
    def test_bad_valid(self):
        print "&&& BAD &&&"
        invalid_rule = UserPolicyStandin(False, "")
        topo = TopologyManager(topology_file=TOPO_CONFIG_FILE)
                               
        engine = BreakdownEngine(CATCH_ERRORS=False)
        self.failUnlessRaises(Exception, engine.get_breakdown, invalid_rule)
        del engine


if __name__ == '__main__':
    unittest.main()
