from __future__ import unicode_literals
# Copyright 2019 - Sean Donovan
# AtlanticWave/SDX Project

from builtins import object
class PathResource(object):
    ''' Represents a resource that a rule needs. This is a parent class, and 
        isn't actually useful by itself. '''

    def __init__(self, name, location, value):
        ''' - name is the name of the type of resource
            - location is the value of the location. It can be a switch, a tuple
              of nodes, whatever.
            - value is the value of the particular resource, such as a VLAN 
              number or amount of bandwidth
        '''

        self._name = name
        self.location = location
        self.value = value
        
    def __repr__(self):
        return "%s : %s,%s,%s" % (self.__class__.__name__,
                                  self._name,
                                  self.location,
                                  self.value)

    def __str__(self):
        retstr = "%s: %s,%s" % (self._name, self.location, self.value)
        return retstr

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.get_location() == other.get_location() and
                self.get_value() == self.get_value())
    
    def get_location(self):
        return self.location

    def get_value(self):
        return self.value

        
class VLANPortResource(PathResource):
    ''' Defines a resource for reserving VLANs on a specified port. '''
    
    def __init__(self, switch, port, vlan):
        super(VLANPortResource, self).__init__("VLAN Port",
                                               (switch, port),
                                               vlan)

    def get_switch(self):
        switch, port = self.location
        return switch
    
    def get_port(self):
        switch, port = self.location
        return port

    def get_vlan(self):
        return self.value

class VLANPathResource(PathResource):
    ''' Defines a resource for reserving VLANs on a specified path. '''
    
    def __init__(self, path, vlan):
        super(VLANPathResource, self).__init__("VLAN Path",
                                               path,
                                               vlan)

    def get_path(self):
        return self.location

    def get_vlan(self):
        return self.value

class VLANTreeResource(PathResource):
    ''' Defines a resource for reserving VLANs on a specified tree. '''
    
    def __init__(self, tree, vlan):
        super(VLANTreeResource, self).__init__("VLAN Tree",
                                               tree,
                                               vlan)

    def get_tree(self):
        return self.location

    def get_vlan(self):
        return self.value

class BandwidthPortResource(PathResource):
    ''' Defines a resource for reserving bandwidth on a specified port. '''
    
    def __init__(self, switch, port, vlan):
        super(BandwidthPortResource, self).__init__("B/W Port",
                                                    (switch, port),
                                                    vlan)
    def get_switch(self):
        switch, port = self.location
        return switch
    
    def get_port(self):
        switch, port = self.location
        return port

    def get_bandwidth(self):
        return self.value

class BandwidthPathResource(PathResource):
    ''' Defines a resource for reserving bandwidth on a specified path. '''
    
    def __init__(self, path, vlan):
        super(BandwidthPathResource, self).__init__("B/W Path",
                                                    path,
                                                    vlan)

    def get_path(self):
        return self.location

    def get_bandwidth(self):
        return self.value

class BandwidthTreeResource(PathResource):
    ''' Defines a resource for reserving bandwidth on a specified tree. '''
    
    def __init__(self, tree, vlan):
        super(BandwidthTreeResource, self).__init__("B/W Tree",
                                                    tree,
                                                    vlan)

    def get_tree(self):
        return self.location

    def get_bandwidth(self):
        return self.value

