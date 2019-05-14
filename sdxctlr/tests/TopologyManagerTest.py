# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the TopologyManager class

import unittest
import threading
#import mock
import networkx as nx

from sdxctlr.TopologyManager import *

CONFIG_FILE = 'test_manifests/topo.manifest'
STEINER_NO_LOOP_CONFIG_FILE = 'test_manifests/steiner-noloop.manifest'
STEINER_LOOP_CONFIG_FILE = 'test_manifests/steiner-loop.manifest'

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

        # This should pass:
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

        man.reserve_bw_on_path(path, 80000000000) 

    def test_reserve_too_much(self):
        man = TopologyManager(CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="atl-switch", target="mia-switch")

        self.failUnlessRaises(Exception, man.reserve_bw_on_path, path, 
                              80000000001)

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

 
class SteinerTreeNoLoopTest(unittest.TestCase):
    ''' +-----+   +-----+   +-----+
        | sw1 |   | sw4 |   | sw6 |
        +--+--+   +--+--+   +--+--+
           |         |         |
        +--+--+   +--+--+   +--+--+
        | sw2 +---+ sw5 +---+ sw7 |
        +--+--+   +-----+   +--+--+
           |                   |
        +--+--+             +--+--+
        | sw3 |             | sw8 |
        +-----+             +-----+
    ''' 

    def test_steiner_tree_no_loop(self):
        man = TopologyManager(STEINER_NO_LOOP_CONFIG_FILE)
        topo = man.get_topology()
        
        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)
        expected_tree_nodes = ["sw1", "sw2", "sw5", "sw6", "sw7", "sw8"]
        returned_tree_nodes = tree.nodes()
        self.failUnlessEqual(len(expected_tree_nodes), 
                             len(returned_tree_nodes))
        for node in expected_tree_nodes:
            self.failUnless(node in returned_tree_nodes)

        # Get a tree connecting sw4, sw8, and sw6
        nodes = ["sw4", "sw6", "sw8"]
        tree = man.find_valid_steiner_tree(nodes)
        expected_tree_nodes = ["sw4", "sw5", "sw6", "sw7", "sw8"]
        returned_tree_nodes = tree.nodes()
        self.failUnlessEqual(len(expected_tree_nodes), 
                             len(returned_tree_nodes))
        for node in expected_tree_nodes:
            self.failUnless(node in returned_tree_nodes)

    def test_find_vlan(self):
        man = TopologyManager(STEINER_NO_LOOP_CONFIG_FILE)
        topo = man.get_topology()
        
        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)

        # Should work
        vlan = man.find_vlan_on_tree(tree)
    
    def test_reserve_vlan(self):
        man = TopologyManager(STEINER_NO_LOOP_CONFIG_FILE)
        topo = man.get_topology()
        
        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)

        # Should work
        vlan = man.find_vlan_on_tree(tree)

        # Should work
        man.reserve_vlan_on_tree(tree, vlan)

    def test_unreserve_vlan(self):
        man = TopologyManager(STEINER_NO_LOOP_CONFIG_FILE)
        topo = man.get_topology()
        
        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)

        # Should work
        vlan = man.find_vlan_on_tree(tree)

        # Should work
        man.reserve_vlan_on_tree(tree, vlan)

        # Should work
        man.unreserve_vlan_on_tree(tree, vlan)

        # Should work
        man.reserve_vlan_on_tree(tree, vlan)

    def test_reserve_on_invalid(self):
        man = TopologyManager(STEINER_NO_LOOP_CONFIG_FILE)
        topo = man.get_topology()
        
        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)

        # Should work
        vlan = man.find_vlan_on_tree(tree)

        # Should work
        man.reserve_vlan_on_tree(tree, vlan)

        # Should work
        self.failUnlessRaises(Exception, man.reserve_vlan_on_tree, tree, vlan)

    def test_reserve_bandwidth(self):
        man = TopologyManager(STEINER_NO_LOOP_CONFIG_FILE)

        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)

        # Should work
        man.reserve_bw_on_tree(tree, 100)
        man.reserve_bw_on_tree(tree, 100)
        man.reserve_bw_on_tree(tree, 100)        


    def test_reserve_maximum(self):
        man = TopologyManager(STEINER_NO_LOOP_CONFIG_FILE)

        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)

        # Should work
        man.reserve_bw_on_tree(tree, 80000000000)

    def test_reserve_too_much(self):
        man = TopologyManager(STEINER_NO_LOOP_CONFIG_FILE)

        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)

        # Should work
        self.failUnlessRaises(Exception, man.reserve_bw_on_tree, tree, 
                              80000000001)

    def test_unreserve_bw(self):
        man = TopologyManager(STEINER_NO_LOOP_CONFIG_FILE)

        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)

        # Should work
        man.reserve_bw_on_tree(tree, 100)
        man.reserve_bw_on_tree(tree, 100)
        man.reserve_bw_on_tree(tree, 100)        

        # Should work
        man.unreserve_bw_on_tree(tree, 100)
        man.unreserve_bw_on_tree(tree, 100)
        man.unreserve_bw_on_tree(tree, 100)        

    def test_unreserve_too_much(self):
        man = TopologyManager(STEINER_NO_LOOP_CONFIG_FILE)

        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)

        # Should work
        man.reserve_bw_on_tree(tree, 100)
        man.unreserve_bw_on_tree(tree, 100)

        self.failUnlessRaises(Exception, man.unreserve_bw_on_tree, tree, 100)

        man.reserve_bw_on_tree(tree, 100)
        self.failUnlessRaises(Exception, man.unreserve_bw_on_tree, tree, 200)


    


class SteinerTreeWithLoopTest(unittest.TestCase):
    ''' +-----+   +-----+   +-----+
        | sw1 |   | sw4 +---+ sw6 |
        +--+--+   +--+--+   +--+--+
           |         |         |
        +--+--+   +--+--+   +--+--+
        | sw2 +---+ sw5 +---+ sw7 |
        +--+--+   +-----+   +--+--+
           |                   |
        +--+--+             +--+--+
        | sw3 +-------------+ sw8 |
        +-----+             +-----+
    '''
    def test_steiner_tree_with_loop(self):
        man = TopologyManager(STEINER_LOOP_CONFIG_FILE)
        topo = man.get_topology()
        
        # Get a tree connecting sw1, sw4, and sw7
        nodes = ['sw1', 'sw4', 'sw7']
        tree = man.find_valid_steiner_tree(nodes)
        expected_tree_nodes = ["sw1", "sw2", "sw5", "sw4", "sw7"]
        returned_tree_nodes = tree.nodes()
        self.failUnlessEqual(len(expected_tree_nodes), 
                             len(returned_tree_nodes))
        for node in expected_tree_nodes:
            self.failUnless(node in returned_tree_nodes)

        # Get a tree connecting sw1, sw3, sw8, sw6
        nodes = ["sw1", "sw3", "sw6", "sw8"]
        tree = man.find_valid_steiner_tree(nodes)
        expected_tree_nodes = ["sw1", "sw2", "sw3", "sw8", "sw7", "sw6"]
        returned_tree_nodes = tree.nodes()
        self.failUnlessEqual(len(expected_tree_nodes), 
                             len(returned_tree_nodes))
        for node in expected_tree_nodes:
            self.failUnless(node in returned_tree_nodes)

        # Get a tree connecting sw1, sw3, sw8
        nodes = ["sw1", "sw3", "sw8"]
        tree = man.find_valid_steiner_tree(nodes)
        expected_tree_nodes = ["sw1", "sw2", "sw3", "sw8"]
        returned_tree_nodes = tree.nodes()
        self.failUnlessEqual(len(expected_tree_nodes), 
                             len(returned_tree_nodes))
        for node in expected_tree_nodes:
            self.failUnless(node in returned_tree_nodes)




if __name__ == '__main__':
    unittest.main()
