# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import SingletonMixin
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

        # Initialize topology lock.
        self.topolock = Lock()

        #FIXME: Static topology right now.
        self._import_topology(topology_file)

    def get_topology(self):
        ''' Returns the topology with all details. 
            This is a NetworkX graph:
            https://networkx.readthedocs.io/en/stable/reference/index.html '''
        return self.topo
    
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

        for key in data['localcontrollers'].keys():
            # Generic per-location information that applies to all switches at
            # a location.
            entry = data['localcontrollers'][key]
            shortname = entry['shortname']
            location = entry['location']
            lcip = entry['lcip']
            org = entry['operatorinfo']['organization']
            administrator = entry['operatorinfo']['administrator']
            contact = entry['operatorinfo']['contact']

            with self.topolock:
                for switchinfo in entry['switchinfo']:
                    name = switchinfo['name']
                    # Node may be implicitly declared, check this first.
                    if not self.topo.has_node(name):
                        self.topo.add_node(name)
                    # Per switch info, gets added to topo
                    self.topo.node[name]['friendlyname'] = switchinfo['friendlyname']
                    self.topo.node[name]['dpid'] = int(switchinfo['dpid'])
                    self.topo.node[name]['ip'] = switchinfo['ip']
                    self.topo.node[name]['brand'] = switchinfo['brand']
                    self.topo.node[name]['model'] = switchinfo['model']
                    self.topo.node[name]['locationshortname'] = shortname
                    self.topo.node[name]['location'] = location
                    self.topo.node[name]['lcip'] = lcip
                    self.topo.node[name]['org'] = org
                    self.topo.node[name]['administrator'] = administrator
                    self.topo.node[name]['contact'] = contact

                    # Other fields that may be of use
                    self.topo.node[name]['vlans_in_use'] = []

                    # Add the links
                    for port in switchinfo['portinfo']:
                        portnumber = int(port['portnumber'])
                        speed = port['speed']
                        destination = port['destination']

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
            is in use at the time at any location. 
            FIXME: This probably has some issues with concurrency. '''
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
                
                
    
