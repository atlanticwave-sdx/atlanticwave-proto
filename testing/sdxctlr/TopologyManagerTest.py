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
        firstManager = TopologyManager.instance(CONFIG_FILE) 
        secondManager = TopologyManager.instance(CONFIG_FILE)

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
        expected_nodes = ['atl-switch', 'mia-switch', 'gru-switch',
                          'atlh1', 'atlh2', 'atldtn',
                          'miah1', 'miah2',
                          'gruh1', 'gruh2', 'grudtn'
                          ]
        nodes = topo.nodes()
        self.failUnless(len(nodes) == len(expected_nodes))
        for node in expected_nodes:
            self.failUnless(node in nodes)

        #FIXME: Need to look at details! In the future, anyway.

        # Should contain
        expected_edges = [('atl-switch', 'mia-switch'),
                          ('mia-switch', 'gru-switch'),
                          ('atl-switch', 'atlh1'),
                          ('atl-switch', 'atlh2'),
                          ('atl-switch', 'atldtn'),
                          ('mia-switch', 'miah1'),
                          ('mia-switch', 'miah2'),
                          ('gru-switch', 'gruh1'),
                          ('gru-switch', 'gruh2'),
                          ('gru-switch', 'grudtn')]
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


class VLANTopoTest(unittest.TestCase):
    
    def test_path_empty(self):
        man = TopologyManager(CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="atl-switch", target="mia-switch")
        
        # It should return 1
        vlan = man.find_vlan_on_path(path)
        self.failUnlessEqual(vlan, 1)

    def test_path_with_node_set(self):
        man = TopologyManager(CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="atl-switch", target="mia-switch")

        # Should return 1
        vlan = man.find_vlan_on_path(path)
        self.failUnlessEqual(vlan, 1)

        # Add VLAN 1 to one of the points on the path
        man.topo.node["mia-switch"]['vlans_in_use'].append(1)
        
        # Should return 2
        vlan = man.find_vlan_on_path(path)
        self.failUnlessEqual(vlan, 2)

    def test_path_with_edge_set(self):
        man = TopologyManager(CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="atl-switch", target="mia-switch")

        # Should return 1
        vlan = man.find_vlan_on_path(path)
        self.failUnlessEqual(vlan, 1)
        
        # Add VLAN 1 to one of the points on the path
        man.topo.edge["mia-switch"]["atl-switch"]['vlans_in_use'].append(1)
        
        # Should return 2
        vlan = man.find_vlan_on_path(path)
        self.failUnlessEqual(vlan, 2)

    def test_path_node_filled(self):
        man = TopologyManager(CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="atl-switch", target="mia-switch")

        # Should return 1
        vlan = man.find_vlan_on_path(path)
        self.failUnlessEqual(vlan, 1)
        
        # Add VLANs 1-4090 to one of the points on the path        
        man.topo.node["mia-switch"]['vlans_in_use'] = range(1,4090)
        
        # Should return None
        vlan = man.find_vlan_on_path(path)
        self.failUnlessEqual(vlan, None)


    def test_path_edge_filled(self):
        man = TopologyManager(CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="atl-switch", target="mia-switch")

        # Should return 1
        vlan = man.find_vlan_on_path(path)
        self.failUnlessEqual(vlan, 1)
        
        # Add VLANs 1-4090 to one of the points on the path        
        man.topo.edge["mia-switch"]["atl-switch"]['vlans_in_use'] = range(1,4090)
        # Should return None
        vlan = man.find_vlan_on_path(path)
        self.failUnlessEqual(vlan, None)

    def test_reserve_on_empty(self):
        man = TopologyManager(CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="atl-switch", target="mia-switch")

        # Reserve path on VLAN 1
        man.reserve_vlan_on_path(path, 1)
        # Should work

    def test_reserve_on_invalid(self):
        # Get a path
        man = TopologyManager(CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="atl-switch", target="mia-switch")
        
        # set VLAN 1 on one of the points on the path
        man.topo.edge["mia-switch"]["atl-switch"]['vlans_in_use'].append(1)

        # Reserve path on VLAN 1
        self.failUnlessRaises(Exception, man.reserve_vlan_on_path, path, 1)
        # Should throw an exception

    def test_unreserve_vlan(self):
        # Get a path
        man = TopologyManager(CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="atl-switch", target="mia-switch")
        
        # Reserve path on VLAN 1
        man.reserve_vlan_on_path(path, 1)

        # Reserve path on VLAN 1
        self.failUnlessRaises(Exception, man.reserve_vlan_on_path, path, 1)
        # Should throw an exception

        # Unreserve path
        man.unreserve_vlan_on_path(path, 1)

        # THis should pass:
        man.reserve_vlan_on_path(path, 1)


class BWTopoTest(unittest.TestCase):

    def test_valid_reservation(self):
        man = TopologyManager(CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="atl-switch", target="mia-switch")

        man.reserve_bw_on_path(path, 100)
        man.reserve_bw_on_path(path, 100)
        man.reserve_bw_on_path(path, 100)
        
    def test_reserve_maximum(self):
        man = TopologyManager(CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="atl-switch", target="mia-switch")

        man.reserve_bw_on_path(path, 1000) 

    def test_reserve_too_much(self):
        man = TopologyManager(CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="atl-switch", target="mia-switch")

        self.failUnlessRaises(Exception, man.reserve_bw_on_path, path, 1001)

    def test_unreserve_reservation(self):
        man = TopologyManager(CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="atl-switch", target="mia-switch")

        man.reserve_bw_on_path(path, 100)
        man.reserve_bw_on_path(path, 100)
        man.reserve_bw_on_path(path, 100)

        man.unreserve_bw_on_path(path, 100)
        man.unreserve_bw_on_path(path, 100)
        man.unreserve_bw_on_path(path, 100)

    def test_unreserve_too_much(self):
        man = TopologyManager(CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="atl-switch", target="mia-switch")

        man.reserve_bw_on_path(path, 100)
        man.unreserve_bw_on_path(path, 100)
        
        self.failUnlessRaises(Exception, man.unreserve_bw_on_path, path, 100)

        man.reserve_bw_on_path(path, 100)
        self.failUnlessRaises(Exception, man.unreserve_bw_on_path, path, 200)

    
if __name__ == '__main__':
    unittest.main()
