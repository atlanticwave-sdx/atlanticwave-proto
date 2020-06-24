from __future__ import absolute_import
# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project


from .LCRule import *

VLAN_MIN = 0
VLAN_MAX = 4095

class LearnedDestinationLCRule(LCRule):
    ''' This structure is used to pass paths to learned destinations around. 
        Created by LearnedDestinationPolicy. '''

    def __init__(self, switch_id, dst_address, outport):
        ''' Field descriptions:
                switch_id - Which switch is involved
                dst_address - The destination address
                outport - Physical port on the switch
        '''
        super(LearnedDestinationLCRule, self).__init__(switch_id)

        # Validate inputs, as much as we can.
        if type(outport) != int:
            raise LCRuleTypeError("outport is not an int: %s, %s" % 
                                  (outport, type(outport)))
        
        # Save off inputs.
        self.dst_address = dst_address
        self.outport = outport
        
    def __str__(self):
        retstr = ("LearnedDestinationLCRule: switch %s, %s:%s:%s" %
                  (self.switch_id, self.cookie,
                   self.dst_address, self.outport))
        return retstr
    
    def __eq__(self, other):
        return (type(self) == type(other) and
                self.get_switch_id() == other.get_switch_id() and
                self.get_cookie() == other.get_cookie() and
                self.get_dst_address() == other.get_dst_address() and
                self.get_outport() == other.get_outport())
    
    def get_dst_address(self):
        return self.dst_address

    def get_outport(self):
        return self.outport

