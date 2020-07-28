from __future__ import absolute_import
from __future__ import unicode_literals
# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project


from shared.LCRule import *

class FloodTreeLCRule(LCRule):
    ''' This structure is used to pass the ports that belong to a spanning tree
        to the Local Controller for handling broadcast flooding without cycles.
        Created by FloodTreePolicy. '''

    def __init__(self, switch_id, ports):
        ''' Field descritpions:
                switch_id - Which switch is involved
                ports - List of ports that are part of the spanning tree needed
                  for broadcast flooding.
        '''
        super(FloodTreeLCRule, self).__init__(switch_id)

        # Validate inputs, as much as we can
        if not (type(ports) == list):
            raise LCRuleTypeError("ports is not a list: %s, %s" %
                                  (ports, type(ports)))

        for port in ports:
            if type(port) != int:
                raise LCRuleTypeError("port in ports is not an int: %s, %s" %
                                      (port, type(port)))

        # Save off inputs
        self.ports = ports

    def __str__(self):
        retstr = ("FloodTreeLCRule: switch %s, %s, (%s)" %
                  (self.switch_id, self.cookie, self.ports))
        return retstr

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.get_switch_id() == other.get_switch_id() and
                self.get_cookie() == other.get_cookie() and
                self.get_ports() == other.get_ports())

    def get_ports(self):
        return self.ports
    
    def get_switch_id(self):
        return self.switch_id

    def get_cookie(self):
        return self.cookie

    def set_ports(self, ports):
        self.ports = ports

    def set_switch_id(self, switch_id):
        self.switch_id = switch_id

    def set_cookie(self, cookie):
        self.cookie = cookie
