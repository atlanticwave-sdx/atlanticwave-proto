# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from lib.Singleton import SingletonMixin
from threading import Lock
import networkx as nx
import json

#FIXME: This shouldn't be hard coded.
MANIFEST_FILE = '../manifests/localcontroller.manifest'

class TopologyManagerError(Exception):
    ''' Parent class as a catch-all for other errors '''
    pass

class TopologyManager(SingletonMixin):
    ''' The TopologyManager handles the topology of the network. Initially, this
        will be very simple, as there will only be three switches, and ~100 
        ports total.
        It may be used to manage virtual topologies (VLANs, for instance) as 
        well.
        It will likely use NetworkX for handling large graphs, as well as for 
        its JSON generation abilities.
        Singleton. '''
    
    def __init__(self, topology_file=MANIFEST_FILE):
        # Initialize topology
        self.topo = nx.Graph()
        self.lcs = []         # This probably should end up as a list of dicts.

        # Initialize topology lock.
        self.topolock = Lock()

        #FIXME: Static topology right now.
        self._import_topology(topology_file)

    def get_topology(self):
        ''' Returns the topology with all details. 
            This is a NetworkX graph:
            https://networkx.readthedocs.io/en/stable/reference/index.html '''
        return self.topo
    
    def get_lcs(self):
        ''' Returns the list of valid LocalControllers. '''
        return self.lcs

    def register_for_topology_updates(self, callback):
        ''' callback will be called when there is a topology update. callback 
            must accept a topology as its only parameter. '''
        # Not used now, as only using static topology.
        pass 
        
    def unregister_for_topology_updates(self, callback):
        ''' Remove callback from list of callbacks to be called when there's a 
            topology update. '''
        # Not used now, as only using static topology.
        pass
    

    def _import_topology(self, manifest_filename):
        with open(manifest_filename) as data_file:
            data = json.load(data_file)

        for key in data['endpoints'].keys():
            # All the other nodes
            endpoint = data['endpoints'][key]
            with self.topolock:
                if not self.topo.has_node(key):
                    self.topo.add_node(key)
                for k in endpoint:
                    if type(endpoint[k]) == int:
                        self.topo.node[key][k] = int(endpoint[k])
                    self.topo.node[key][k] = str(endpoint[k])
                    

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
                for switchinfo in entry['switchinfo']:
                    name = switchinfo['name']
                    # Node may be implicitly declared, check this first.
                    if not self.topo.has_node(name):
                        self.topo.add_node(name)
                    # Per switch info, gets added to topo
                    self.topo.node[name]['friendlyname'] = switchinfo['friendlyname']
                    self.topo.node[name]['dpid'] = int(switchinfo['dpid'], 0) #0 guesses base.
                    self.topo.node[name]['ip'] = str(switchinfo['ip'])
                    self.topo.node[name]['brand'] = str(switchinfo['brand'])
                    self.topo.node[name]['model'] = str(switchinfo['model'])
                    self.topo.node[name]['locationshortname'] = shortname
                    self.topo.node[name]['location'] = location
                    self.topo.node[name]['lcip'] = lcip
                    self.topo.node[name]['org'] = org
                    self.topo.node[name]['administrator'] = administrator
                    self.topo.node[name]['contact'] = contact
                    self.topo.node[name]['type'] = "switch"

                    # Other fields that may be of use
                    self.topo.node[name]['vlans_in_use'] = []

                    # Add the links
                    for port in switchinfo['portinfo']:
                        portnumber = int(port['portnumber'])
                        speed = str(port['speed'])
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
                        
                    

    def find_vlan_on_path(self, path):
        ''' Finds a VLAN that's not being used at the moment on a provided path.
            Returns an available VLAN if possible, None if none are available on
            the submitted path.
        '''
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
                    
                if on_path:
                    continue

                # If all good, set selected_vlan
                selected_vlan = vlan
                break

        return selected_vlan
    
    def reserve_vlan_on_path(self, path, vlan):
        ''' Marks a VLAN in use on a provided path. Raises an error if the VLAN
            is in use at the time at any location. '''
        #FIXME: Should there be some more accounting on this? Reference to the
        #structure reserving the vlan?
        # FIXME: This probably has some issues with concurrency.

        with self.topolock:
            # Make sure the path is clear -> very similar to find_vlan_on_path
            for point in path:
                if vlan in self.topo.node[point]['vlans_in_use']:
                    raise TopologyManagerError("VLAN %d is already reserved on node %s" % (vlan, point))

            for (node, nextnode) in zip(path[0:-1], path[1:]):
                if vlan in self.topo.edge[node][nextnode]['vlans_in_use']:
                    raise TopologyManagerError("VLAN %d is already reserved on path %s:%s" % (vlan, node, nextnode))                    

            # Walk through the points and reserve it
            for point in path:
                self.topo.node[point]['vlans_in_use'].append(vlan)

            # Walk through the edges and reserve it
            for (node, nextnode) in zip(path[0:-1], path[1:]):
                self.topo.edge[node][nextnode]['vlans_in_use'].append(vlan)

    def unreserve_vlan_on_path(self, path, vlan):
        ''' Removes reservations on a given path for a given VLAN. '''
        with self.topolock:
            # Make sure it's already reserved on the given path:
            for point in path:
                if vlan not in self.topo.node[point]['vlans_in_use']:
                    raise TopologyManagerError("VLAN %d is not reserved on node %s" % (vlan, point))

            for (node, nextnode) in zip(path[0:-1], path[1:]):
                if vlan not in self.topo.edge[node][nextnode]['vlans_in_use']:
                    raise TopologyManagerError("VLAN %d is not reserved on path %s:%s" % (vlan, node, nextnode))

            # Walk through teh points and unreserve it
            for point in path:
                self.topo.node[point]['vlans_in_use'].remove(vlan)

            # Walk through the edges and unreserve it
            for (node, nextnode) in zip(path[0:-1], path[1:]):
                self.topo.edge[node][nextnode]['vlans_in_use'].remove(vlan)
                
        pass

    def reserve_bw_on_path(self, path, bw):
        ''' Reserves a specified amount of bandwidth on a given path. Raises an
            error if the bandwidth is not available at any part of the path. '''
        #FIXME: Should there be some more accounting on this? Reference to the
        #structure reserving the bw?

        with self.topolock:
            # Check to see if we're going to go over the bandwidth of the edge
            for (node, nextnode) in zip(path[0:-1], path[1:]):
                bw_in_use = self.topo.edge[node][nextnode]['bw_in_use']
                bw_available = int(self.topo.edge[node][nextnode]['weight'])

                if (bw_in_use + bw) > bw_available:
                    raise TopologyManagerError("BW available on path %s:%s is %s. In use %s, new reservation of %s" % (node, nextnode, bw_available, bw_in_use, bw))

            # Add bandwidth reservation
            for (node, nextnode) in zip(path[0:-1], path[1:]):
                self.topo.edge[node][nextnode]['bw_in_use'] += bw

    def unreserve_bw_on_path(self, path, bw):
        ''' Removes reservations on a given path for a given amount of
            bandwidth. '''
        with self.topolock:
            # Check to see if we've removed too much
            for (node, nextnode) in zip(path[0:-1], path[1:]):
                bw_in_use = self.topo.edge[node][nextnode]['bw_in_use']

                if bw > bw_in_use:
                    raise TopologyManagerError("BW in use on path %s:%s is %s. Trying to remove %s" % (node, nextnode, bw_in_use, bw))

            # Remove bw from path
            for (node, nextnode) in zip(path[0:-1], path[1:]):
                self.topo.edge[node][nextnode]['bw_in_use'] -= bw


    def find_valid_path(self, src, dst, bw=None):
        ''' Find a path that is currently valid based on a contstraint. 
            Right now, the only constraint is bandwidth. '''

        # Get possible paths
        #FIXME: NetworkX has multiple methods for getting paths. Shortest and
        # all possible paths:
        # https://networkx.readthedocs.io/en/stable/reference/generated/networkx.algorithms.shortest_paths.generic.all_shortest_paths.html
        # https://networkx.readthedocs.io/en/stable/reference/generated/networkx.algorithms.simple_paths.all_simple_paths.html
        # May need to use *both* algorithms. Starting with shortest paths now.
        list_of_paths = nx.all_shortest_paths(self.topo,
                                              source=src,
                                              target=dst)

        for path in list_of_paths:
            # For each path, check that a VLAN is available
            vlan = self.find_vlan_on_path(path)
            if vlan == None:
                continue

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
                return path
        
        # No path return
        return None
