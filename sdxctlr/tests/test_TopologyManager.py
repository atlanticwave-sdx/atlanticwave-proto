from __future__ import print_function
from __future__ import unicode_literals
# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the TopologyManager class

from builtins import range
import unittest
import threading
#import mock
import networkx as nx

from sdxctlr.TopologyManager import *

CONFIG_FILE = 'tests/test_manifests/topo.manifest'
STEINER_NO_LOOP_CONFIG_FILE = 'tests/test_manifests/steiner-noloop.manifest'
STEINER_LOOP_CONFIG_FILE = 'tests/test_manifests/steiner-loop.manifest'

class SingletonTest(unittest.TestCase):
    def test_singleton(self):
        firstManager = TopologyManager(topology_file=CONFIG_FILE) 
        secondManager = TopologyManager(topology_file=CONFIG_FILE)

        self.assertTrue(firstManager is secondManager)

class VerifyTopoTest(unittest.TestCase):
    def setUp(self):
        man = TopologyManager(topology_file=CONFIG_FILE)
        man.topo = nx.Graph()
        man._import_topology(CONFIG_FILE)
        
    def test_get_topo(self):
        man = TopologyManager(topology_file=CONFIG_FILE)
        topo = man.get_topology()
        self.assertTrue(isinstance(topo, nx.Graph))
        
    def test_simple_topo(self):
        man = TopologyManager(topology_file=CONFIG_FILE)
        topo = man.get_topology()

        expected_nodes = ['br1', 'br2', 'br3', 'br4',
                          'br1dtn1', 'br1dtn2',
                          'br2dtn1', 'br2dtn2', 'br2dtn3',
                          'br3dtn1',
                          'br4dtn1', 'br4dtn2',
                          'oneLC'] # The LC counts as a node, just in case.
        nodes = topo.nodes()
        #print "\nNODES : %s" % nodes
        #print "EXPECT: %s" % expected_nodes
        self.assertEquals(len(nodes), len(expected_nodes))
        for node in expected_nodes:
            self.assertTrue(node in nodes)

        #FIXME: Need to look at details! In the future, anyway.

        # Should contain
        expected_edges = [
            ('br1', 'br1dtn1'), ('br1', 'br1dtn2'),
            ('br2', 'br2dtn1'), ('br2', 'br2dtn2'), ('br2', 'br2dtn3'),
            ('br3', 'br3dtn1'),
            ('br4', 'br4dtn1'), ('br4', 'br4dtn2'),
            ('br1', 'br2'), ('br1', 'br3'),
            ('br2', 'br3'),
            ('br3', 'br4')]
        edges = topo.edges()

        self.assertTrue(len(edges) == len(expected_edges))
        for edge in expected_edges:
            (a, b) = edge
            reversed_edge = (b,a)
            # We don't care about ordering of the edges)
            # Both options below end up with same result.
            self.assertTrue((edge in edges) or (reversed_edge in edges))
            self.assertTrue(topo.has_edge(a, b))

        #import json
        #print json.dumps(topo.nodes(data=True), indent=1)
        #print "\n\n"
        #print json.dumps(topo.edges(data=True), indent=1)


class VLANTopoTest(unittest.TestCase):
    def setUp(self):
        man = TopologyManager(topology_file=CONFIG_FILE)
        man.topo = nx.Graph()
        man._import_topology(CONFIG_FILE)
        
    
    def test_path_empty(self):
        man = TopologyManager(topology_file=CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="br1", target="br4")
        print(path)
        # It should return 10
        vlan = man.find_vlan_on_path(path)
        print("vlan="+str(vlan))
        self.assertEqual(vlan, 10)

    def test_path_with_node_set(self):
        man = TopologyManager(topology_file=CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="br4", target="br1")
        print(path)
        # Should return 10
        vlan = man.find_vlan_on_path(path)
        print("vlan="+str(vlan))
        self.assertEqual(vlan, 10)

        # Add VLAN 10 to one of the points on the path
        vlan=10
        for (node, nextnode) in zip(path[0:-1], path[1:]):
            man.topo.edge[node][nextnode]['vlans_in_use'].append(vlan)
            man.topo.node[node]['vlans_in_use'].append(vlan)
        
        # Should return None
        path = nx.shortest_path(topo, source="br4dtn1", target="br1dtn1")
        print(path)
        vlans = man.find_vlans_on_path(path)
        print("vlans="+str(vlans))
        self.assertNotEqual(vlans, None)
        # Remove VLAN 10 to one of the points on the path
        for (node, nextnode) in zip(path[1:-2], path[2:]):
            man.topo.edge[node][nextnode]['vlans_in_use'].remove(vlan)
            man.topo.node[node]['vlans_in_use'].remove(vlan)

    def test_path_with_edge_set(self):
        man = TopologyManager(topology_file=CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="br2", target="br4")
        print("path="+str(path))
        # Should return 10
        vlan = man.find_vlan_on_path(path)
        self.assertEqual(vlan, 10)
        
        # Add VLAN 10 to one of the points on the path
        print("\n%s" % man.topo.edge['br3']['br4'])
        man.topo.edge["br3"]["br4"]['vlans_in_use'].append(10)
        print(man.topo.edge['br3']['br4'])
        
        # Should return 2
        vlans = man.find_vlans_on_path(path)
        print("vlans="+str(vlans))
        self.assertNotEqual(vlan, None)
        man.topo.edge["br3"]["br4"]['vlans_in_use'].remove(10)

    def test_path_node_filled(self):
        man = TopologyManager(topology_file=CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="br4", target="br3")

        # Should return 1
        vlan = man.find_vlan_on_path(path)
        self.assertEqual(vlan, 1)
        
        # Add VLANs 1-4090 to one of the points on the path        
        man.topo.node["br4"]['vlans_in_use'] = list(range(1,4090))
        
        # Should return None
        vlan = man.find_vlan_on_path(path)
        self.assertEqual(vlan, None)
        man.topo.node["br4"]['vlans_in_use'] = []


    def test_path_edge_filled(self):
        man = TopologyManager(topology_file=CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="br4", target="br1")

        # Should return 1
        vlan = man.find_vlan_on_path(path)
        self.assertEqual(vlan, 1)
        
        # Add VLANs 1-4090 to one of the points on the path        
        man.topo.edge["br4"]["br3"]['vlans_in_use'] = list(range(1,4090))
        # Should return None
        vlan = man.find_vlan_on_path(path)
        self.assertEqual(vlan, None)
        man.topo.edge["br4"]["br3"]['vlans_in_use'] = []

    def test_reserve_on_empty(self):
        man = TopologyManager(topology_file=CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="br4", target="br1")

        # Reserve path on VLAN 1
        man.reserve_vlan_on_path(path, 1)
        # Should work

    def test_reserve_on_invalid(self):
        # Get a path
        man = TopologyManager(topology_file=CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="br4", target="br1")
        
        # set VLAN 1 on one of the points on the path
        man.topo.edge["br4"]["br3"]['vlans_in_use'].append(1)

        # Reserve path on VLAN 1
        self.assertRaises(Exception, man.reserve_vlan_on_path, path, 1)
        # Should throw an exception

    def test_unreserve_vlan(self):
        # Get a path
        man = TopologyManager(topology_file=CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="br4", target="br3")
        
        # Reserve path on VLAN 100
        man.reserve_vlan_on_path(path, 100)

        # Reserve path on VLAN 100
        self.assertRaises(Exception, man.reserve_vlan_on_path, path, 100)
        # Should throw an exception

        # Unreserve path
        man.unreserve_vlan_on_path(path, 100)

        # This should pass:
        man.reserve_vlan_on_path(path, 100)


class BWTopoTest(unittest.TestCase):
    def setUp(self):
        man = TopologyManager(topology_file=CONFIG_FILE)
        man.topo = nx.Graph()
        man._import_topology(CONFIG_FILE)
        
    def test_valid_reservation(self):
        man = TopologyManager(topology_file=CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="br4", target="br1")

        man.reserve_bw_on_path(path, 100)
        man.reserve_bw_on_path(path, 100)
        man.reserve_bw_on_path(path, 100)
        
    def test_reserve_maximum(self):
        man = TopologyManager(topology_file=CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="br4", target="br3")

        man.reserve_bw_on_path(path, 8000000000)
        man.unreserve_bw_on_path(path, 8000000000)

    def test_reserve_too_much(self):
        man = TopologyManager(topology_file=CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="br4", target="br2")

        self.assertRaises(Exception, man.reserve_bw_on_path, path, 
                              8000000001)

    def test_unreserve_reservation(self):
        man = TopologyManager(topology_file=CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="br4", target="br1")

        man.reserve_bw_on_path(path, 100)
        man.reserve_bw_on_path(path, 100)
        man.reserve_bw_on_path(path, 100)

        man.unreserve_bw_on_path(path, 100)
        man.unreserve_bw_on_path(path, 100)
        man.unreserve_bw_on_path(path, 100)

    def test_unreserve_too_much(self):
        man = TopologyManager(topology_file=CONFIG_FILE)
        topo = man.get_topology()

        # Get a path
        path = nx.shortest_path(topo, source="br4", target="br3")

        man.reserve_bw_on_path(path, 100)
        man.unreserve_bw_on_path(path, 100)
        
        self.assertRaises(Exception, man.unreserve_bw_on_path, path, 100)

        man.reserve_bw_on_path(path, 100)
        self.assertRaises(Exception, man.unreserve_bw_on_path, path, 200)

 
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

    def setUp(self):
        man = TopologyManager(topology_file=STEINER_NO_LOOP_CONFIG_FILE)
        man.topo = nx.Graph()
        man._import_topology(STEINER_NO_LOOP_CONFIG_FILE)

    def test_steiner_tree_no_loop(self):
        man = TopologyManager(topology_file=STEINER_NO_LOOP_CONFIG_FILE)
        topo = man.get_topology()
        
        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)
        expected_tree_nodes = ["sw1", "sw2", "sw5", "sw6", "sw7", "sw8"]
        returned_tree_nodes = tree.nodes()
        self.assertEqual(len(expected_tree_nodes), 
                             len(returned_tree_nodes))
        for node in expected_tree_nodes:
            self.assertTrue(node in returned_tree_nodes)

        # Get a tree connecting sw4, sw8, and sw6
        nodes = ["sw4", "sw6", "sw8"]
        tree = man.find_valid_steiner_tree(nodes)
        expected_tree_nodes = ["sw4", "sw5", "sw6", "sw7", "sw8"]
        returned_tree_nodes = tree.nodes()
        self.assertEqual(len(expected_tree_nodes), 
                             len(returned_tree_nodes))
        for node in expected_tree_nodes:
            self.assertTrue(node in returned_tree_nodes)

    def test_find_vlan(self):
        man = TopologyManager(topology_file=STEINER_NO_LOOP_CONFIG_FILE)
        topo = man.get_topology()
        
        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)

        # Should work
        vlan = man.find_vlan_on_tree(tree)
    
    def test_reserve_vlan(self):
        man = TopologyManager(topology_file=STEINER_NO_LOOP_CONFIG_FILE)
        topo = man.get_topology()
        
        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)

        # Should work
        vlan = man.find_vlan_on_tree(tree)

        # Should work
        man.reserve_vlan_on_tree(tree, vlan)

    def test_unreserve_vlan(self):
        man = TopologyManager(topology_file=STEINER_NO_LOOP_CONFIG_FILE)
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
        man = TopologyManager(topology_file=STEINER_NO_LOOP_CONFIG_FILE)
        topo = man.get_topology()
        
        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)

        # Should work
        vlan = man.find_vlan_on_tree(tree)

        # Should work
        man.reserve_vlan_on_tree(tree, vlan)

        # Should work
        self.assertRaises(Exception, man.reserve_vlan_on_tree, tree, vlan)

    def test_reserve_bandwidth(self):
        man = TopologyManager(topology_file=STEINER_NO_LOOP_CONFIG_FILE)

        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)

        # Should work
        man.reserve_bw_on_tree(tree, 100)
        man.reserve_bw_on_tree(tree, 100)
        man.reserve_bw_on_tree(tree, 100)        
        man.unreserve_bw_on_tree(tree, 100)
        man.unreserve_bw_on_tree(tree, 100)
        man.unreserve_bw_on_tree(tree, 100)        


    def test_reserve_maximum(self):
        man = TopologyManager(topology_file=STEINER_NO_LOOP_CONFIG_FILE)

        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)

        # Should work
        man.reserve_bw_on_tree(tree, 80000000000)
        man.unreserve_bw_on_tree(tree, 80000000000)

    def test_reserve_too_much(self):
        man = TopologyManager(topology_file=STEINER_NO_LOOP_CONFIG_FILE)

        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)

        # Should work
        self.assertRaises(Exception, man.reserve_bw_on_tree, tree, 
                              80000000001)

    def test_unreserve_bw(self):
        man = TopologyManager(topology_file=STEINER_NO_LOOP_CONFIG_FILE)

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
        man = TopologyManager(topology_file=STEINER_NO_LOOP_CONFIG_FILE)

        # Get a tree connecting sw1, sw8, and sw6
        nodes = ['sw1', 'sw8', 'sw6']
        tree = man.find_valid_steiner_tree(nodes)

        # Should work
        man.reserve_bw_on_tree(tree, 100)
        man.unreserve_bw_on_tree(tree, 100)

        self.assertRaises(Exception, man.unreserve_bw_on_tree, tree, 100)

        man.reserve_bw_on_tree(tree, 100)
        self.assertRaises(Exception, man.unreserve_bw_on_tree, tree, 200)
        man.unreserve_bw_on_tree(tree, 100)

    


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
    def setUp(self):
        man = TopologyManager(topology_file=STEINER_LOOP_CONFIG_FILE)
        man.topo = nx.Graph()
        man._import_topology(STEINER_LOOP_CONFIG_FILE)

    def test_steiner_tree_with_loop(self):
        man = TopologyManager(topology_file=STEINER_LOOP_CONFIG_FILE)
        topo = man.get_topology()
        
        # Get a tree connecting sw1, sw4, and sw7
        nodes = ['sw1', 'sw4', 'sw7']
        tree = man.find_valid_steiner_tree(nodes)
        expected_tree_nodes = ["sw1", "sw2", "sw5", "sw4", "sw7"]
        returned_tree_nodes = tree.nodes()
        self.assertEqual(len(expected_tree_nodes), 
                             len(returned_tree_nodes))
        for node in expected_tree_nodes:
            self.assertTrue(node in returned_tree_nodes)

        # Get a tree connecting sw1, sw3, sw8, sw6
        nodes = ["sw1", "sw3", "sw6", "sw8"]
        tree = man.find_valid_steiner_tree(nodes)
        expected_tree_nodes = ["sw1", "sw2", "sw3", "sw8", "sw7", "sw6"]
        returned_tree_nodes = tree.nodes()
        self.assertEqual(len(expected_tree_nodes), 
                             len(returned_tree_nodes))
        for node in expected_tree_nodes:
            self.assertTrue(node in returned_tree_nodes)

        # Get a tree connecting sw1, sw3, sw8
        nodes = ["sw1", "sw3", "sw8"]
        tree = man.find_valid_steiner_tree(nodes)
        expected_tree_nodes = ["sw1", "sw2", "sw3", "sw8"]
        returned_tree_nodes = tree.nodes()
        self.assertEqual(len(expected_tree_nodes), 
                             len(returned_tree_nodes))
        for node in expected_tree_nodes:
            self.assertTrue(node in returned_tree_nodes)




if __name__ == '__main__':
    unittest.main()
