from __future__ import absolute_import
# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from .LCRule import *

VLAN_MIN = 0
VLAN_MAX = 4095

class VlanTunnelLCRule(LCRule):
    ''' This structure is used to pass Rules that create VLANs between two ports
        on a switch. Connection can be unidirectional or bidirectional.'''

    def __init__(self, switch_id, inport, outport, vlan_in, vlan_out, 
                 bidirectional=True, bandwidth=None):
        ''' Field descriptions:
                inport - Physical port on the switch
                outport - Physical port on the switch
                vlan_in - VLAN in use on the in-port
                vlan_out - VLAN in use on the out-port
                bidirectional - Boolean describing if the connection should be 
                    bidirectional or unidirectional.
                bandwidth - Bandwidth requirement in megabits-per-second. None 
                    means there is no specific requirement.
        '''
        super(VlanTunnelLCRule, self).__init__(switch_id)

        # Validate inputs, as much as we can.
        if type(inport) != int:
            raise LCRuleTypeError("inport is not an int: %s, %s" % 
                                  (inport, type(inport)))
        if type(outport) != int:
            raise LCRuleTypeError("outport is not an int: %s, %s" % 
                                  (outport, type(outport)))
        if type(vlan_in) != int:
            raise LCRuleTypeError("vlan_in is not an int: %s, %s" % 
                                  (vlan_in, type(vlan_in)))
        if type(vlan_out) != int:
            raise LCRuleTypeError("vlan_out is not an int: %s, %s" % 
                                  (vlan_out, type(vlan_out)))
        if not (type(bandwidth) == int or bandwidth == None):
            raise LCRuleTypeError("bandwidth is not an int or None: %s, %s" % 
                                  (bandwidth, type(bandwidth)))
        if type(bidirectional) != bool:
            raise LCRuleTypeError("bidirectional is not a bool: %s, %s" % 
                                  (bidirectional, type(bidirectional)))
        if (vlan_in < VLAN_MIN) or (vlan_in > VLAN_MAX):
            raise LCRuleValueError("vlan_in is not in valid range (%s,%s): %s" %
                                   (VLAN_MIN, VLAN_MAX, vlan_in))
        if (vlan_out < VLAN_MIN) or (vlan_out > VLAN_MAX):
            raise LCRuleValueError("vlan_out is not in valid range (%s,%s): %s" %
                                   (VLAN_MIN, VLAN_MAX, vlan_out))

        
        # Save off inputs.
        self.inport = inport
        self.outport = outport
        self.vlan_in = vlan_in
        self.vlan_out = vlan_out
        self.bidirectional = bidirectional
        self.bandwidth = bandwidth
        
    def __str__(self):
        retstr = ("VlanTunnelLCRule: switch %s, %s:%s:%s:%s:%s:%s:%s" % 
                  (self.switch_id, self.cookie,
                   self.inport, self.outport,
                   self.vlan_in, self.vlan_out,
                   self.bidirectional, self.bandwidth))
        return retstr

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.get_switch_id() == other.get_switch_id() and
                self.get_cookie() == other.get_cookie() and
                self.get_inport() == other.get_inport() and
                self.get_outport() == other.get_outport() and
                self.get_vlan_in() == other.get_vlan_in() and
                self.get_vlan_out() == other.get_vlan_out() and
                self.get_bidirectional() == other.get_bidirectional() and
                self.get_bandwidth() == other.get_bandwidth())                
                
        

    def get_inport(self):
        return self.inport

    def get_outport(self):
        return self.outport

    def get_vlan_in(self):
        return self.vlan_in

    def get_vlan_out(self):
        return self.vlan_out

    def get_bidirectional(self):
        return self.bidirectional

    def get_bandwidth(self):
        return self.bandwidth
