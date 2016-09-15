# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton
import networkx as nx
import json

#FIXME: This shouldn't be hard coded.
MANIFEST_FILE = '../manifests/localcontroller.manifest'

class TopologyManager(object):
    ''' The TopologyManager handles the topology of the network. Initially, this 
        will be very simple, as there will only be three switches, and ~100 ports
        total.
        It may be used to manage virtual topologies (VLANs, for instance) as 
        well.
        It will likely use NetworkX for handling large graphs, as well as for its
        JSON generation abilities.
        Singleton. '''
    __metaclass__ = Singleton
    
    def __init__(self, topology_file=MANIFEST_FILE):
        # Initialize topology
        self.topo = nx.Graph()

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

            for switchinfo in entry['switchinfo']:
                name = switchinfo['name']
                # Node may be implicitly declared, check this first.
                if not self.topo.has_node(name):
                    self.topo.add_node(name)
                # Per switch info, gets added to topo
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

                # Add the links
                for port in switchinfo['portinfo']:
                    portnumber = int(port['portnumber'])
                    speed = port['speed']
                    destination = port['destination']

                    # If link already exists
                    if not self.topo.has_edge(name, destination):
                        self.topo.add_edge(name, destination, weight = speed)
                    # Set the port number for the current location. The dest port
                    # should be set when the dest side has been run.
                    self.topo.edge[name][destination][name] = portnumber
                    

                    
                
                
    
