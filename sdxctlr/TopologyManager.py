# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton

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
    
    def __init__(self):
        pass

    def get_topology(self):
        ''' Returns the topology with all details. '''
        pass
    
    def register_for_topology_updates(self, callback):
        ''' callback will be called when there is a topology update. callback 
            must accept a topology as its only parameter. '''
        pass
        
    def unregister_for_topology_updates(self, callback):
        ''' Remove callback from list of callbacks to be called when there’s a 
            topology update. '''
        pass
    

