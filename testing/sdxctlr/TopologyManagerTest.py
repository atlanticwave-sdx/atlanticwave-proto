# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the TopologyManager class

import unittest
import threading
#import mock
import networkx as nx

from sdxctlr.TopologyManager import *

CONFIG_FILE = 'test_manifests/topo.manifest'

class SingletonTest(unittest.TestCase):
    def test_singleton(self):
        firstManager = TopologyManager(CONFIG_FILE) 
        secondManager = TopologyManager(CONFIG_FILE)

        self.failUnless(firstManager is secondManager)

class VerifyTopoTest(unittest.TestCase):
    def test_get_topo(self):
        man = TopologyManager(CONFIG_FILE)
        topo = man.get_topology()
        self.failUnless(isinstance(topo, nx.Graph))
        
    def test_simple_topo(self):
        man = TopologyManager(CONFIG_FILE)
        topo = man.get_topology()

        # Should contain: atl-switch, mia-switch, Georgia Tech, FIU
        expected_nodes = ['atl-switch', 'mia-switch', 'Georgia Tech', 'FIU']
        nodes = topo.nodes()
        self.failUnless(len(nodes) == len(expected_nodes))
        for node in expected_nodes:
            self.failUnless(node in nodes)

        #FIXME: Need to look at details! In the future, anyway.

        # Should contain
        expected_edges = [('Georgia Tech', 'atl-switch'),
                          ('atl-switch', 'mia-switch'),
                          ('mia-switch', 'FIU')]
        edges = topo.edges()
        self.failUnless(len(edges) == len(expected_edges))
        for edge in expected_edges:
            (a, b) = edge
            reversed_edge = (b,a)
            # We don't care about ordering of the edges)
            # Both options below end up with same result.
            self.failUnless((edge in edges) or (reversed_edge in edges))
            self.failUnless(topo.has_edge(a, b))

        #import json
        #print json.dumps(topo.nodes(data=True), indent=1)
        #print "\n\n"
        #print json.dumps(topo.edges(data=True), indent=1)

if __name__ == '__main__':
    unittest.main()
