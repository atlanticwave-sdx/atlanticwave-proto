from __future__ import print_function
# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from lib.AtlanticWaveManager import AtlanticWaveManager
from threading import Lock
from datetime import datetime
import networkx as nx
import json
from lib.SteinerTree import make_steiner_tree
from shared.PathResource import *

from shared.constants import rfc3339format
#FIXME: This shouldn't be hard coded.
MANIFEST_FILE = '../manifests/localcontroller.manifest'

# Define different node types
NODE_TYPE_MIN         = 1
NODE_SWITCH           = 1
NODE_LC               = 2
NODE_SDX              = 3
NODE_HOST             = 4
NODE_DTN              = 5
NODE_NETWORK          = 6
NODE_TYPE_MAX         = 6


def TOPO_TYPE_TO_STRING(typenum):
    if typenum == NODE_SWITCH:
        return "switch"
    elif typenum == NODE_LC:
        return "localcontroller"
    elif typenum == NODE_SDX:
        return "sdxcontroller"
    elif typenum == NODE_HOST:
        return "host"
    elif typenum == NODE_DTN:
        return "dtn"
    elif typenum == NODE_NETWORK:
        return "network"

def TOPO_VALID_TYPE(typestr):
    if (typestr == "switch" or
        typestr == "localcontroller" or
        typestr == "sdxcontroller" or
        typestr == "host" or
        typestr == "dtn" or
        typestr == "network"):
        return True
    return False

def TOPO_EDGE_TYPE(typestr):
    ''' Used to identify edge connections. Used by API(s). '''
    if (typestr == 'dtn' or
        typestr == 'network'):
        return True
    return False

class TopologyManagerError(Exception):
    ''' Parent class as a catch-all for other errors '''
    pass

class TopologyManagerTypeError(TypeError):
    pass

class TopologyManagerValueError(ValueError):
    pass

class TopologyManager(AtlanticWaveManager):
    ''' The TopologyManager handles the topology of the network. Initially, this
        will be very simple, as there will only be three switches, and ~100 
        ports total.
        It may be used to manage virtual topologies (VLANs, for instance) as 
        well.
        It will likely use NetworkX for handling large graphs, as well as for 
        its JSON generation abilities.
        Singleton. '''
    
    def __init__(self, loggeridprefix='sdxcontroller',
                 topology_file=MANIFEST_FILE):
        loggerid = loggeridprefix + ".topologymanager"
        super(TopologyManager, self).__init__(loggerid)
        
        # Initialize topology
        self.topo = nx.Graph()
        self.lcs = []         # This probably should end up as a list of dicts.

        # Initialize topology lock.
        self.topolock = Lock()

        # So we don't have to parse VLANs over an over again
        self._cached_vlans = {}

        # Last modified timestamp
        now = datetime.now()
        self.last_modified = now.strftime(rfc3339format)
            
        #FIXME: Static topology right now.
        self._import_topology(topology_file)

        # List of all topology update callbacks
        self.topology_update_callbacks = []

        self.logger.warning("%s initialized: %s" % (self.__class__.__name__,
                                                    hex(id(self))))

    def get_topology(self):
        ''' Returns the topology with all details. 
            This is a NetworkX graph:
            https://networkx.readthedocs.io/en/stable/reference/index.html '''
        return self.topo
    
    def get_lcs(self):
        ''' Returns the list of valid LocalControllers. '''
        return self.lcs

    def _update_last_modified_timestamp(self):
        ''' Used for setting the last_modified timestamp. '''
        now = datetime.now()
        self.last_modified = now.strftime(rfc3339format)

    def get_last_modified_timestamp(self):
        ''' Get the last_modified timestamp. '''
        return self.last_modified

    def register_for_topology_updates(self, callback):
        ''' callback will be called when there is a topology update. callback 
            must accept a topology as its only parameter. '''
        # Not used now, as only using static topology.
        if callback != None:
            self.topology_update_callbacks.append(callback)
        
    def unregister_for_topology_updates(self, callback):
        ''' Remove callback from list of callbacks to be called when there's a 
            topology update. '''
        # Not used now, as only using static topology.
        if callback != None:
            try:
                self.topology_update_callbacks.remove(callback)
            except:
                raise TopologyManagerError("Trying to remove %s, not in topology_update_callbacks: %s" % (callback, self.topology_update_callbacks))

    def _call_topology_update_callbacks(self, change):
        ''' FIXME: This isn't used yet. ''' 
        for cb in self.topology_update_callbacks:
            cb(change)

    def _import_topology(self, manifest_filename):
        with open(manifest_filename) as data_file:
            data = json.load(data_file)

        for unikey in data['endpoints'].keys():
            # All the other nodes
            key = str(unikey)
            endpoint = data['endpoints'][key]
            #FIXME: Validation?
            with self.topolock:
                if not self.topo.has_node(key):
                    self.topo.add_node(key)
                for k in endpoint:
                    if k == "type" and not TOPO_VALID_TYPE(endpoint[k]):
                        raise TopologyManagerError("Invalid type string %s" %
                                                   endpoint[k])
                    elif type(endpoint[k]) == int:
                        self.topo.node[key][k] = int(endpoint[k])
                    self.topo.node[key][k] = str(endpoint[k])
                # Add other required fields to the endpoitn dict
                self.topo.node[key]['vlans_in_use'] = []
                    

        for key in data['localcontrollers'].keys():
            # Generic per-location information that applies to all switches at
            # a location.
            # FIXME: Everything's wrapped as a str or int because Unicode.
            entry = data['localcontrollers'][key]
            shortname = str(entry['shortname'])
            location = str(entry['location'])
            lcip = str(entry['lcip'])
            org = str(entry['operatorinfo']['organization'])
            administrator = str(entry['operatorinfo']['administrator'])
            contact = str(entry['operatorinfo']['contact'])
            
            # Add shortname to the list of valid LocalControllers
            self.lcs.append(shortname)

            # Fill out topology
            with self.topolock:
                # Add local controller
                self.topo.add_node(str(key))
                self.topo.node[key]['type'] = "localcontroller"
                self.topo.node[key]['shortname'] = shortname
                self.topo.node[key]['location'] = location
                self.topo.node[key]['ip'] = lcip
                self.topo.node[key]['org'] = org
                self.topo.node[key]['administrator'] = administrator
                self.topo.node[key]['contact'] = contact
                self.topo.node[key]['internalconfig'] = entry['internalconfig']

                # Add switches to the local controller. Actually happens after
                # the switches are handled.
                switch_list = []

                # Switches for that LC
                for switchinfo in entry['switchinfo']:
                    name = str(switchinfo['name'])
                    # Node may be implicitly declared, check this first.
                    if not self.topo.has_node(name):
                        self.topo.add_node(name)

                    # Add switch to LC list. This will be added at the end.
                    switch_list.append(name)
                    
                    # Per switch info, gets added to topo
                    self.topo.node[name]['friendlyname'] = str(switchinfo['friendlyname'])
                    self.topo.node[name]['dpid'] = int(switchinfo['dpid'], 0) #0 guesses base.
                    self.topo.node[name]['ip'] = str(switchinfo['ip'])
                    self.topo.node[name]['brand'] = str(switchinfo['brand'])
                    self.topo.node[name]['model'] = str(switchinfo['model'])
                    self.topo.node[name]['locationshortname'] = shortname
                    self.topo.node[name]['location'] = location
                    self.topo.node[name]['lcip'] = lcip
                    self.topo.node[name]['lcname'] = key
                    self.topo.node[name]['org'] = org
                    self.topo.node[name]['administrator'] = administrator
                    self.topo.node[name]['contact'] = contact
                    self.topo.node[name]['type'] = "switch"

                    # Other fields that may be of use
                    self.topo.node[name]['vlans_in_use'] = []

                    self.topo.node[name]['internalconfig'] = switchinfo['internalconfig']

                    # Add the links
                    for port in switchinfo['portinfo']:
                        portnumber = int(port['portnumber'])
                        speed = int(port['speed'])
                        destination = str(port['destination'])

                        # If link already exists
                        if not self.topo.has_edge(name, destination):
                            self.topo.add_edge(name,
                                               destination,
                                               weight=speed)
                        # Set the port number for the current location. The dest
                        # port should be set when the dest side has been run.
                        self.topo.edge[name][destination][name] = portnumber

                        # Other fields that may be of use
                        self.topo.edge[name][destination]['vlans_in_use'] = []
                        self.topo.edge[name][destination]['bw_in_use'] = 0

                        # VLANs available
                        if 'available_vlans' in port.keys():
                            self.topo.edge[name][destination]['available_vlans'] = str(port['available_vlans'])
                        elif 'available_vlans' in self.topo.node[port['destination']].keys():
                            self.topo.edge[name][destination]['available_vlans'] = str(self.topo.node[port['destination']]['available_vlans'])
                        else:
                            self.topo.edge[name][destination]['available_vlans'] = "0-4095"

                # Once all the switches have been looked at, add them to the
                # LC
                self.topo.node[key]['switches'] = switch_list

    # -----------------
    # Generic functions
    # -----------------

    def check_vlan_available(self, vlan_str, vlan):
        if vlan_str not in self._cached_vlans.keys():
            self._parse_available_vlans(vlan_str)
        valid_vlans = self._cached_vlans[vlan_str]

        return vlan in valid_vlans        

    def get_available_vlan_list(self, vlan_str):
        if vlan_str not in self._cached_vlans.keys():
            self._parse_available_vlans(vlan_str)
        return self._cached_vlans[vlan_str]
    
    def _parse_available_vlans(self, vlan_str):
        valid_vlans = []
        ranges = vlan_str.split(",")
        for r in ranges:
            r_parts = r.split("-")
            if len(r_parts) == 1:
                if type(int(r_parts[0])) != int:
                    raise TopologyManagerTypeError(
                        "Available VLAN type error %s:%s" %
                        (type(r_parts[0]), r_parts[0]))
                elif int(r_parts[0]) < 0 or int(r_parts[0]) > 4095:
                    raise TopologyManagerValueError(
                        "Available VLAN out of range: %s" %
                        r_parts[0])
                valid_vlans.append(int(r_parts[0]))
            elif len(r_parts) == 2:
                low = int(r_parts[0])
                high = int(r_parts[1])
                if type(low) != int:
                    raise TopologyManagerTypeError(
                        "Available VLAN type error %s:%s" %
                        (type(low), low))
                elif type(high) != int:
                    raise TopologyManagerTypeError(
                        "Available VLAN type error %s:%s" %
                        (type(low), low))
                elif low < 0 or low > 4095:
                    raise TopologyManagerValueError(
                        "Available VLAN out of range: %s" %
                        low)
                elif high < 0 or high > 4095:
                    raise TopologyManagerValueError(
                        "Available VLAN out of range: %s" %
                        high)
                elif low > high:
                    raise TopologyManagerValueError(
                        "Available VLANs out of order: %s-%s" %
                        (low, high))

                for x in range(low, high+1):
                    valid_vlans.append(x)

        self._cached_vlans[vlan_str] = valid_vlans

    def reserve_bw(self, node_pairs, bw):        
        ''' Generic method for reserving bandwidth based on pairs of nodes. '''
        #FIXME: Should there be some more accounting on this? Reference to the
        #structure reserving the bw?
        self.dlogger.debug("reserve_bw: %s, %s" % (bw, node_pairs))
        with self.topolock:
            # Check to see if we're going to go over the bandwidth of the edge
            for (node, nextnode) in node_pairs:
                bw_in_use = self.topo.edge[node][nextnode]['bw_in_use']
                bw_available = int(self.topo.edge[node][nextnode]['weight'])

                if (bw_in_use + bw) > bw_available:
                    raise TopologyManagerError("BW available on path %s:%s is %s. In use %s, new reservation of %s" % (node, nextnode, bw_available, bw_in_use, bw))

            # Add bandwidth reservation
            for (node, nextnode) in node_pairs:
                self.topo.edge[node][nextnode]['bw_in_use'] += bw

    def unreserve_bw(self, node_pairs, bw):
        ''' Generic method for removing bw reservation based on pairs of nodes. 
        '''
        self.dlogger.debug("unreserve_bw: %s, %s" % (bw, node_pairs))
        with self.topolock:
            # Check to see if we've removed too much
            for (node, nextnode) in node_pairs:
                bw_in_use = self.topo.edge[node][nextnode]['bw_in_use']

                if bw > bw_in_use:
                    raise TopologyManagerError("BW in use on path %s:%s is %s. Trying to remove %s" % (node, nextnode, bw_in_use, bw))

            # Remove bw from path
            for (node, nextnode) in node_pairs:
                self.topo.edge[node][nextnode]['bw_in_use'] -= bw

    def reserve_vlan(self, nodes, node_pairs, vlan):
        ''' Generic method for reserving VLANs on given nodes and paths based on
            nodes and pairs of nodes. '''
        #FIXME: Should there be some more accounting on this? Reference to the
        #structure reserving the vlan?
        # FIXME: This probably has some issues with concurrency.
        self.dlogger.debug("reserve_vlan: %s, %s" % (vlan, node_pairs))
        with self.topolock:
            # Make sure the path is clear -> very similar to find_vlan_on_path
            for node in nodes:
                print("\nself.topo.node[%s]: %s\n" % (node, self.topo.node[node]))
                if vlan in self.topo.node[node]['vlans_in_use']:
                    raise TopologyManagerError("VLAN %d is already reserved on node %s" % (vlan, node))

            for (node, nextnode) in node_pairs:
                if vlan in self.topo.edge[node][nextnode]['vlans_in_use']:
                    raise TopologyManagerError("VLAN %d is already reserved on path %s:%s" % (vlan, node, nextnode))                    

            # Walk through the nodess and reserve it
            for node in nodes:
                self.topo.node[node]['vlans_in_use'].append(vlan)

            # Walk through the edges and reserve it
            for (node, nextnode) in node_pairs:
                self.topo.edge[node][nextnode]['vlans_in_use'].append(vlan)
    
    def unreserve_vlan(self, nodes, node_pairs, vlan):
        ''' Generic method for unreserving VLANs on given nodes and paths based 
            on nodes and pairs of nodes. '''
        self.dlogger.debug("unreserve_vlan: %s, %s" % (vlan, node_pairs))
        with self.topolock:
            # Make sure it's already reserved on the given path:
            for node in nodes:
                if vlan not in self.topo.node[node]['vlans_in_use']:
                    raise TopologyManagerError("VLAN %d is not reserved on node %s" % (vlan, node))

            for (node, nextnode) in node_pairs:
                if vlan not in self.topo.edge[node][nextnode]['vlans_in_use']:
                    raise TopologyManagerError("VLAN %d is not reserved on path %s:%s" % (vlan, node, nextnode))

            # Walk through the nodes and unreserve it
            for node in nodes:
                self.topo.node[node]['vlans_in_use'].remove(vlan)

            # Walk through the edges and unreserve it
            for (node, nextnode) in node_pairs:
                self.topo.edge[node][nextnode]['vlans_in_use'].remove(vlan)

    def reserve_resource(self, resource):
        ''' Reserve the requested resource. '''
        if isinstance(resource, VLANPortResource):
            self.reserve_vlan_on_port(resource.get_switch(),
                                      resource.get_port(),
                                      resource.get_vlan())
        elif isinstance(resource, VLANPathResource):
            self.reserve_vlan_on_path(resource.get_path(),
                                      resource.get_vlan())
        elif isinstance(resource, VLANTreeResource):
            self.reserve_vlan_on_tree(resource.get_tree(),
                                      resource.get_vlan())
        elif isinstance(resource, BandwidthPortResource):
            self.reserve_bw_on_port(resource.get_switch(),
                                           resource.get_port(),
                                           resource.get_bandwidth())
        elif isinstance(resource, BandwidthPathResource):
            self.reserve_bw_on_path(resource.get_path(),
                                           resource.get_bandwidth())
        elif isinstance(resource, BandwidthTreeResource):
            self.reserve_bw_on_tree(resource.get_tree(),
                                           resource.get_bandwidth())
        else:
            raise TopologyManagerTypeError(
                "%s is not a valid resource to reserve. %s" % (
                type(resource), resource))
        
    def unreserve_resource(self, resource):
        ''' Release the requested resource. '''
        if isinstance(resource, VLANPortResource):
            self.unreserve_vlan_on_port(resource.get_switch(),
                                        resource.get_port(),
                                        resource.get_vlan())
        elif isinstance(resource, VLANPathResource):
            self.unreserve_vlan_on_path(resource.get_path(),
                                        resource.get_vlan())
        elif isinstance(resource, VLANTreeResource):
            self.unreserve_vlan_on_tree(resource.get_tree(),
                                        resource.get_vlan())
        elif isinstance(resource, BandwidthPortResource):
            self.unreserve_bw_on_port(resource.get_switch(),
                                             resource.get_port(),
                                             resource.get_bandwidth())
        elif isinstance(resource, BandwidthPathResource):
            self.unreserve_bw_on_path(resource.get_path(),
                                             resource.get_bandwidth())
        elif isinstance(resource, BandwidthTreeResource):
            self.unreserve_bw_on_tree(resource.get_tree(),
                                             resource.get_bandwidth())
        else:
            raise TopologyManagerTypeError(
                "%s is not a valid resource to unreserve. %s" % (
                type(resource), resource))
                
    # --------------
    # Path functions
    # --------------

    def reserve_vlan_on_path(self, path, vlan):
        ''' Marks a VLAN in use on a provided path. Raises an error if the VLAN
            is in use at the time at any location. '''
        node_pairs = zip(path[0:-1], path[1:])
        self.reserve_vlan(path, node_pairs, vlan)
        
    def unreserve_vlan_on_path(self, path, vlan):
        ''' Removes reservations on a given path for a given VLAN. '''
        node_pairs = zip(path[0:-1], path[1:])
        self.unreserve_vlan(path, node_pairs, vlan)

    def reserve_bw_on_path(self, path, bw):
        ''' Reserves a specified amount of bandwidth on a given path. Raises an
            error if the bandwidth is not available at any part of the path. '''
        node_pairs = zip(path[0:-1], path[1:])
        self.reserve_bw(node_pairs, bw)
        
    def unreserve_bw_on_path(self, path, bw):
        ''' Removes reservations on a given path for a given amount of
            bandwidth. '''
        node_pairs = zip(path[0:-1], path[1:])
        self.unreserve_bw(node_pairs, bw)

    def find_vlan_on_path(self, path):
        ''' Finds a VLAN that's not being used at the moment on a provided path.
            Returns an available VLAN if possible, None if none are available on
            the submitted path.
        '''
        self.dlogger.debug("find_vlan_on_path: %s" % path)
        selected_vlan = None
        with self.topolock:
            for vlan in range(1,4089):
                # Check each point on the path
                on_path = False
                for point in path:
                    if self.topo.node[point]["type"] == "switch":
                        if vlan in self.topo.node[point]['vlans_in_use']:
                            on_path = True
                            break
                if on_path:
                    continue

                # Check each edge on the path
                for (node, nextnode) in zip(path[0:-1], path[1:]):
                    if vlan in self.topo.edge[node][nextnode]['vlans_in_use']:
                        on_path = True
                        break
                    if vlan not in self.get_available_vlan_list(
                            self.topo.edge[node][nextnode]['available_vlans']):
                        on_path = True
                        break
                    
                if on_path:
                    continue

                # If all good, set selected_vlan
                selected_vlan = vlan
                break
            
        self.dlogger.debug("find_vlan_on_path returning %s" % selected_vlan)
        return selected_vlan

    def find_valid_path(self, src, dst, bw=None, ignore_endpoints=False):
        ''' Find a path that is currently valid based on a contstraint. 
            Right now, the only constraint is bandwidth. 
            ignore_endpoints is for ignoring the path all the way to the 
            endpoints themselves when checking constraints, and just verifying
            at all other points. Returns stripped path (all middle points). This
            is for cases when there *could* be multiple paths from a given 
            endpoint, we don't want to artifically restrict possible paths. '''

        # Get possible paths
        #FIXME: NetworkX has multiple methods for getting paths. Shortest and
        # all possible paths:
        # https://networkx.readthedocs.io/en/stable/reference/generated/networkx.algorithms.shortest_paths.generic.all_shortest_paths.html
        # https://networkx.readthedocs.io/en/stable/reference/generated/networkx.algorithms.simple_paths.all_simple_paths.html
        # May need to use *both* algorithms. Starting with shortest paths now.
        self.dlogger.debug("find_valid_path: %s, %s, %s" % (bw, src, dst))
        list_of_paths = nx.all_shortest_paths(self.topo,
                                              source=src,
                                              target=dst)

        for path in list_of_paths:
            # For each path, check that a VLAN is available
            if ignore_endpoints:
                path = path[1:-1]
            vlan = self.find_vlan_on_path(path)
            if vlan == None:
                continue
            
            self.dlogger.debug("find_valid_path found path %s has valid VLANs" %
                                   path)
            enough_bw = True
            for (node, nextnode) in zip(path[0:-1], path[1:]):
                # For each edge on the path, check that bw is available.
                bw_in_use = self.topo.edge[node][nextnode]['bw_in_use']
                bw_available = int(self.topo.edge[node][nextnode]['weight'])

                if (bw_in_use + bw) > bw_available:
                    enough_bw = False
                    break
                
            # If all's good, return the path to the caller
            if enough_bw:
                self.dlogger.debug("find_valid_path found path has bw %s" %
                                   path)
                return path
        
        # No path return
        self.dlogger.debug("find_valid_path found no path")
        return None

    
    # --------------
    # Tree functions
    # --------------

    def reserve_vlan_on_tree(self, tree, vlan):
        ''' Marks a VLAN in use on a provided tree (nx graph). Raises an error 
            if the VLAN is in use at the time at any location. '''
        self.reserve_vlan(tree.nodes(), tree.edges(), vlan)
        
    def unreserve_vlan_on_tree(self, tree, vlan):
        ''' Removes reservations on a given tree (nx graph) for a given VLAN. 
        '''
        self.unreserve_vlan(tree.nodes(), tree.edges(), vlan)

    def reserve_bw_on_tree(self, tree, bw):
        ''' Reserves a specified amount of bandwidth on a given tree (nx graph).
            Raises an error if the bandwidth is not available at any part of the
            tree. '''
        self.reserve_bw(tree.edges(), bw)
        
    def unreserve_bw_on_tree(self, tree, bw):
        ''' Removes reservations on a given tree (nx graph) for a given amount 
            of bandwidth. '''
        self.unreserve_bw(tree.edges(), bw)

    def find_vlan_on_tree(self, tree):
        ''' Tree version of find_vlan_on_path(). Finds a VLAN that's not being
            used at the moment on a provivded path. Returns an available VLAN if
            possible, None if none are available on the submitted tree. '''
        self.dlogger.debug("find_vlan_on_tree: %s" % tree.nodes()) 
        selected_vlan = None
        with self.topolock:
            for vlan in range(1,4089):
                # Check each point on the path
                on_path = False
                for node in tree.nodes():
                    if self.topo.node[node]["type"] == "switch":
                        if vlan in self.topo.node[node]['vlans_in_use']:
                            on_path = True
                            break
                    
                if on_path:
                    continue

                # Check each edge on the path
                for (node, nextnode) in tree.edges():
                    if vlan in self.topo.edge[node][nextnode]['vlans_in_use']:
                        on_path = True
                        break
                    
                if on_path:
                    continue

                # If all good, set selected_vlan
                selected_vlan = vlan
                break

        self.dlogger.debug("find_vlan_on_tree returning %s" % selected_vlan)
        return selected_vlan

    def find_valid_steiner_tree(self, nodes, bw=None):
        ''' Finds a Steiner tree connecting all the nodes in 'nodes' together. 
            Uses a library containing Kou's algorithm to find one. 
            Returns a graph, from with .nodes() and .edges() can be used
            to call other functions. '''

        #FIXME: need to accomodate inability to find appropriate amount of
        #bandwidth. Take existing topology, copy it, and delete the edge with
        #a problem, then rerun Kou's algorithm.

        self.dlogger.debug("find_valid_steiner_tree: %s, %s" % (bw, nodes))
        # Prime the topology to use
        topo = self.topo
        # Loop through, trying to make a valid Steiner tree that has available
        # bandwidth. This will either return something valid, or will blow up
        # due to a path not existing and will return nothing.
        # timeout is a just-in-case measure
        timeout = len(topo.edges())
        while(timeout > 0):
            timeout -= 1
            
            try:
                tree = make_steiner_tree(self.topo, nodes)
                self.dlogger.debug("find_valid_steiner_tree: found %s" %
                                   (tree.edges()))

            except ValueError:
                raise
            except nx.exception.NetworkXNoPath:
                #FIXME: log something here.
                return None

            # Check if enough bandwidth is available
            enough_bw = True
            for (node, nextnode) in tree.edges():
                # For each edge on the path, check that bw is available.
                bw_in_use = self.topo.edge[node][nextnode]['bw_in_use']
                bw_available = int(self.topo.edge[node][nextnode]['weight'])

                if bw is not None and (bw_in_use + bw) > bw_available:
                    enough_bw = False
                    # Remove the edge that doesn't have enough bw and try again
                    topo.remove_edge(node, nextnode)
                    break
            if not enough_bw:
                continue
                

            # Check if VLAN is available
            selected_vlan = self.find_vlan_on_tree(tree)
            if selected_vlan == None:
                #FIXME: how to handle this?
                self.logger.error("find_valid_steiner_tree: Could not find VLAN, unhandled!")
                pass
 

            # Has BW and VLAN available, return it.
            self.dlogger.debug("find_valid_steiner_tree: Successful %s" %
                               tree.edges())
            return tree
            
    # -------------------
    # Port-only functions
    # -------------------

    def get_switch_port_neighbor(self, switchname, portnum):
        ''' Finds a neighbor for a switch/port combination.
            returns name of neighbor if exists, None if it doesn't.
        '''
        # Check if port is in use: loop through neighbors
        for neighbor in self.topo[switchname].keys():
            # - if neighbor is using that port, good, we have a match
            if self.topo[switchname][neighbor][switchname] == portnum:
                # --return neighbor name
                return neighbor
        return None

    def reserve_vlan_on_port(self, switchname, portnum, vlan):
        ''' Reserves VLANs on a specific port. '''
        neighbor = self.get_switch_port_neighbor(switchname, portnum)
        if neighbor != None:
            # - reserve the VLAN on both sides of the connection
            self.dlogger.debug("reserve_vlan_on_port: %s,%s,%s" % (
                switchname, neighbor, vlan))
            # We're not reserving on the switch, as that should already
            # be covered.
            self.reserve_vlan([], [(switchname, neighbor)], vlan)
        # No worries if there were no matches!

    def unreserve_vlan_on_port(self, switchname, portnum, vlan):
        ''' Releases VLANs on a specific port. '''
        neighbor = self.get_switch_port_neighbor(switchname, portnum)
        if neighbor != None:
            # - unreserve the VLAN on both sides of the connection, but not
            # on the switch itself: we only care about the port right now.
            self.dlogger.debug("unreserve_vlan_on_port: %s,%s,%s" % (
                switchname, neighbor, vlan))
            self.unreserve_vlan([],[(switchname, neighbor)], vlan)
        # No worries if there were no matches!

    def reserve_bw_on_port(self, switchname, portnum, bw):
        ''' Reserves bandwidth on a specific port. '''
        neighbor = self.get_switch_port_neighbor(switchname, portnum)
        if neighbor != None:
            # - reserve the bandwidth on both sides of the connection
            self.dlogger.debug("reserve_bw_on_port: %s,%s,%s" % (
                switchname, neighbor, bw))
            self.reserve_bw([(switchname, neighbor)], bw)
        # No worries if there were no matches!

    def unreserve_bw_on_port(self, switchname, portnum, bw):
        ''' Releases bandwidth on a specific port. '''
        neighbor = self.get_switch_port_neighbor(switchname, portnum)
        if neighbor != None:
            # - unreserve the bandwidth on both sides of the connection
            self.dlogger.debug("unreserve_bw_on_port: %s,%s,%s" % (
                switchname, neighbor, bw))
            self.unreserve_bw([(switchname, neighbor)], bw)
        # No worries if there were no matches!

