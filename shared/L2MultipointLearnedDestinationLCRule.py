from __future__ import absolute_import
# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project


from .LCRule import *

VLAN_MIN = 0
VLAN_MAX = 4095

class L2MultipointLearnedDestinationLCRule(LCRule):
    ''' This structure is used to pass paths to learned destinations around. 
        Created by L2MultipointPolicy. '''

    def __init__(self, switch_id, dst_address, outport,
                 intermediate_vlan, out_vlan):
        ''' Field descriptions:
                switch_id - Which switch is involved
                dst_address - The destination address
                outport - Physical port on the switch
                intermediate_vlan - Intermediate VLAN used by the 
                  L2MultipointPolicy across its Steiner Tree
                out_vlan - VLAN for output. For non-destinations switches,
                  this will be the Intermediate VLAN, but there is required 
                  translation at the destination switch.
        '''
        super(L2MultipointLearnedDestinationLCRule, self).__init__(switch_id)

        # Validate inputs, as much as we can.
        if type(outport) != int:
            raise LCRuleTypeError("outport is not an int: %s, %s" % 
                                  (outport, type(outport)))

        if type(intermediate_vlan) != int:
            raise LCRuleTypeError("intermediate_vlan is not an int: %s, %s" % 
                                  (intermediate_vlan, type(intermediate_vlan)))

        if (intermediate_vlan < VLAN_MIN) or (intermediate_vlan > VLAN_MAX):
            raise LCRuleTypeError("intermediate_vlan is not in valid range (%s,%s): %s" %
                                  (VLAN_MIN, VLAN_MAX, intermediate_vlan))
        
        if type(out_vlan) != int:
            raise LCRuleTypeError("out_vlan is not an int: %s, %s" % 
                                  (out_vlan, type(out_vlan)))

        if (out_vlan < VLAN_MIN) or (out_vlan > VLAN_MAX):
            raise LCRuleTypeError("out_vlan is not in valid range (%s,%s): %s" %
                                  (VLAN_MIN, VLAN_MAX, out_vlan))
        
        
        # Save off inputs.
        self.dst_address = dst_address
        self.outport = outport
        self.intermediate_vlan = intermediate_vlan
        self.out_vlan = out_vlan
        
    def __str__(self):
        retstr = ("L2MultipointLearnedDestinationLCRule: switch %s, %s:%s:%s" %
                  (self.switch_id, self.cookie,
                   self.dst_address, self.outport))
        return retstr

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.get_switch_id() == other.get_switch_id() and
                self.get_cookie() == other.get_cookie() and
                self.get_dst_address() == other.get_dst_address() and
                self.get_outport() == other.get_outport() and
                self.get_intermediate_vlan() == other.get_intermediate_vlan() and
                self.get_out_vlan() == other.get_out_vlan())
    
    def get_dst_address(self):
        return self.dst_address

    def get_outport(self):
        return self.outport

    def get_intermediate_vlan(self):
        return self.intermediate_vlan

    def get_out_vlan(self):
        return self.out_vlan
