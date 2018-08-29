# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project

from lib.AtlanticWaveModule import AtlanticWaveModule

from shared.L2MultipointPolicy import L2MultipointPolicy
from shared.L2TunnelPolicy import L2TunnelPolicy

from AuthenticationInspector import AuthenticationInspector
from AuthorizationInspector import AuthorizationInspector
from RuleManager import RuleManager
from TopologyManager import TopologyManager, TOPO_EDGE_TYPE
from UserManager import UserManager
from RuleRegistry import RuleRegistry

from threading import Lock

# XML imports


# Other imports
import networkx as nx
from networkx.readwrite import json_graph
import json

# Multithreading
from threading import Thread

class SenseAPI(AtlanticWaveModule):
    ''' The SenseAPI is the main interface for SENSE integration. It generates
        the appropriate XML for the current configuration status, and sends 
        updates automatically based on changes in rules and topology as provided
        by the RuleManager and TopologyManager.
    '''

    def __init__(self, loggerprefix='sdxcontroller',
                 host='0.0.0.0', port=5001):
        loggerid = loggerprefix + ".sense"
        super(SenseAPI, self).__init__(loggerid)

        # Set up local repositories for rules and topology to perform diffs on.
        self.current_rules = RuleManager().get_rules()
        self.current_topo = TopologyManager().get_topology()
        self.simplified_topo = None
        self.topo_XML = None
        self.delta_XML = None
        self.topolock = Lock()
        self.userid = "SENSE"
        
        # Register update functions
        RuleManager().register_for_rule_updates(self.rule_add_callback,
                                                self.rule_rm_callback)
        TopologyManager().register_for_topology_updates(
            self.topo_change_callback)

        #
        
        # Connection handling
        #FIXME - Is it inbound or outbound?

        

        self.logger.warning("%s initialized: %s" % (self.__class__.__name__,
                                                    hex(id(self))))

        self._INTERNAL_TESTING_DELETE_FINAL_CHECKIN()

    def _INTERNAL_TESTING_DELETE_FINAL_CHECKIN(self):
        nodes = self.current_topo.nodes()
        print("\n\nNODES WITH DETAILS\n" +
              json.dumps(self.current_topo.nodes(data=True),
                                    indent=4, sort_keys=True))
        print "\n\nEDGES\n" + str(self.current_topo.edges()) + "\n\n\n"
        for node in nodes:
            print "  %s : %s" % (node, self.current_topo[node])
        for node in nodes:
            print "\n%s:%s " % (node, json.dumps(self.current_topo[node],
                                                    indent=4, sort_keys=True))
        self.generate_simplified_topology()
        for node in self.simplified_topo.nodes():
            if self.simplified_topo.node[node]['type'] != 'central':
                self.get_bw_available_on_egress_port(node)
                self.get_vlans_in_use_on_egress_port(node)

        for srcnode in self.simplified_topo.nodes():
            if self.simplified_topo.node[srcnode]['type'] != 'central':
                for dstnode in self.simplified_topo.nodes():
                    if self.simplified_topo.node[dstnode]['type'] != 'central':
                        self.install_point_to_point_rule(srcnode, dstnode,
                                                    100, 200,
                                                    100000,
                                                    "1985-04-12T12:34:56",
                                                    "2985-04-12T12:34:56")
        
    def rule_add_callback(self, rule):
        ''' Handles rules being added. '''
        pass

    def rule_rm_callback(self, rule):
        ''' Handles rules being removed. '''
        pass

    def topo_change_callback(self):
        ''' Handles topology changes. 
            FIXME: topologies don't change right now. '''
        pass

    def get_bw_available_on_egress_port(self, node):
        ''' Get the bandwidth available on a given egress port from the original
            network graph. Be sure to update topology before making these 
            requests. '''

        # Access the bandwidth from the original topology.
        print self.simplified_topo.node[node]
        start_node = self.simplified_topo.node[node]['start_node']
        end_node = self.simplified_topo.node[node]['end_node']
        bw_available = self.simplified_topo.node[node]['max_bw']
        bw_in_use = self.current_topo[start_node][end_node]['bw_in_use']

        print "%s: bw_available %s, bw_in_use %s" % (node, bw_available,
                                                     bw_in_use)
        # Return BW on egress port
        return (bw_available - bw_in_use)

    def get_vlans_in_use_on_egress_port(self, node):
        ''' Get the VLANs that are in use on a given egress port. '''

        # Access the bandwidth from the original topology.
        print self.simplified_topo.node[node]
        start_node = self.simplified_topo.node[node]['start_node']
        end_node = self.simplified_topo.node[node]['end_node']
        vlans_in_use = self.current_topo[start_node][end_node]['vlans_in_use']

        print "%s: vlans_in_use %s" % (node, vlans_in_use)

        # Return VLANs in use on egress port
        return vlans_in_use

    def get_vlans_available_on_egress_port(self, node):
        ''' Get VLANs available for SENSE API use. '''
        pass

    def generate_simplified_topology(self):
        ''' Calculates the 'black box' version of the topology, exposing only 
            the outside networks and DTNs as endpoints. The internals are *not*
            exposed, as we handle those ourselves. '''
        
        # Create graph with central node only.
        with self.topolock:
            self.simplified_topo = nx.Graph()
            self.simplified_topo.add_node('central')
            self.simplified_topo.node['central']['type'] = 'central'

            # For each EDGE node (returns true on TOPO_EDGE_TYPE), loop over
            # each connection on the edge node add a connection to the central
            # node.
            for node in self.current_topo.nodes(): # name of node
                print self.current_topo[node]
                t = self.current_topo.node[node]['type']
                if TOPO_EDGE_TYPE(t):
                    for edge in self.current_topo[node]: # edge dictionary
                        new_node = node + "-" + edge
                        self.simplified_topo.add_node(new_node)

                        # Copy over how to access the connection (which two
                        # nodes on the original topology), and the max bandwidth
                        # of the connection.                    
                        self.simplified_topo.node[new_node]['start_node'] = node
                        self.simplified_topo.node[new_node]['end_node'] = edge
                        print self.current_topo[node][edge]
                        bw = self.current_topo[node][edge]['weight']
                        self.simplified_topo.node[new_node]['max_bw'] = bw
                        self.simplified_topo.node[new_node]['type'] = t
        print("\n\nSIMPLIFIED TOPOLOGY\n%s\n\n" %
              json.dumps(self.simplified_topo.nodes(data=True),
                         indent=4, sort_keys=True))
                                                    

    def generate_full_XML(self):
        ''' Generates the full XML of the simplified topology. Deltas are 
            handled separately. '''
        pass

    def generate_delta_XML(self, change):
        ''' Generates a delta based on a change passed in.
              - Topology change
              - Bandwidth change (up or down)
        '''
        pass

    def install_point_to_point_rule(self, endpoint1, endpoint2, vlan1, vlan2,
                                    bandwidth, starttime, endtime):
        ''' Installs a point-to-point rule. '''

        # Find the src switch and switch port
        src = self.simplified_topo.node[endpoint1]['start_node']
        srcswitch = self.simplified_topo.node[endpoint1]['end_node']
        srcport = self.current_topo[srcswitch][src][srcswitch]
        print "SRC %s switch %s port %s" % (src, srcswitch, srcport)

        # FInd the dst switch and switch port
        dst = self.simplified_topo.node[endpoint2]['start_node']
        dstswitch = self.simplified_topo.node[endpoint2]['end_node']
        dstport = self.current_topo[dstswitch][dst][dstswitch]
        print "DST %s switch %s port %s" % (dst, dstswitch, dstport)
        
        # Make JSON version
        jsonrule = {"L2Tunnel":{
            "starttime":starttime,
            "endtime":endtime,
            "srcswitch":srcswitch,
            "dstswitch":dstswitch,
            "srcport":srcport,
            "dstport":dstport,
            "srcvlan":vlan1,
            "dstvlan":vlan2,
            "bandwidth":bandwidth}}
        print "\nJSON\n%s" % (json.dumps(jsonrule, indent=4, sort_keys=True))
        
        # Perform check_syntax
        L2TunnelPolicy.check_syntax(jsonrule)

        # Make policy class
        policy = L2TunnelPolicy(self.userid, jsonrule)

        # Install rule
        hash = RuleManager().add_rule(policy)

        #FIXME: What should be returned?
        #FIXME: What to do about Exceptions?
        pass
    
    def install_point_to_multipoint_rule(self, endpointvlantuplelist,
                                         bandwidth,  starttime, endtime):
        ''' Installs a point-to-multipoint rule. '''
        #FIXME: When should this be done?
        # Make JSON version
        
        # Perform check_syntax

        # Make policy class

        # Install rule

        #FIXME: What should be returned?
        pass


    def connection_thread(self):
        pass

    def handle_new_connection(self):
        pass
