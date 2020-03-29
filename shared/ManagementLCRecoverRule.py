# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project

from LCRule import *

class ManagementLCRecoverRule(LCRule):
    ''' This structure is used to pass the ports that belong to a spanning tree
        to the Local Controller for handling broadcast flooding without cycles.
        Created by FloodTreePolicy. '''

    def __init__(self, cookie, switch_id):
        ''' Field descritpions:
                switch_id - Which switch is involved
                ports - List of ports that are part of the spanning tree needed
                  for broadcast flooding.
        '''
        super(ManagementLCRecoverRule, self).__init__(self, switch_id)
        self.cookie = cookie
        self.switch_id = switch_id

    def __str__(self):
        retstr = ("ManagementLCRecoverRule: switch %s" %
                  (self.switch_id))
        return retstr

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.get_switch_id() == other.get_switch_id())
    
    def get_switch_id(self):
        return self.switch_id

    def get_cookie(self):
        return self.cookie
