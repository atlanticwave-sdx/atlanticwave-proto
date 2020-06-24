from __future__ import absolute_import
# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project


from .LCRule import *

VLAN_MIN = 0
VLAN_MAX = 4095

class L2MultipointFloodLCRule(LCRule):
    ''' This structure is used to pass L2Multpoint rules for intermediate 
        switches. If an endpoint exists on a switch, L2MultipointEndpointLCRule 
        will be used. 
        Created by L2MultipointPolicy. '''

    def __init__(self, switch_id, flooding_ports, intermediate_vlan):
        ''' Field descriptions:
                switch_id - Which switch is involved
                flooding_ports - List of ports connected to the endpoint switch 
                  that are not endpoint ports. Flooding-only port on the 
                  intermediate VLAN. Can be None, if endpoints are located solely
                  on one switch.
                intermediate_vlan - VLAN used for traffic between endpoint ports.
                  Can be None, if endpoints are located solely on one switch.
        '''
        super(L2MultipointFloodLCRule, self).__init__(switch_id)

        # Validate inputs, as much as we can.
        if not (type(flooding_ports) == None or type(flooding_ports) == list):
            raise LCRuleTypeError("flooding_ports is not None or a list: %s, %s" % 
                                  (flooding_ports, type(flooding_ports)))
        for port in flooding_ports:
            if type(port) != int:
                raise LCRuleTypeError("port in flooding_ports is not an int: %s, %s" % 
                                  (port, type(port)))

        if type(intermediate_vlan) != int:
            raise LCRuleTypeError("intermediate_vlan is not an int: %s, %s" %
                                      (intermediate_vlan,
                                       type(intermediate_vlan)))
                
        # Save off inputs.
        self.flooding_ports = flooding_ports
        self.intermediate_vlan = intermediate_vlan
        
    def __str__(self):
        retstr = ("L2MultipointFloodLCRule: switch %s, %s:(%s), %s" %
                  (self.switch_id, self.cookie, self.flooding_ports,
                   self.intermediate_vlan))
        return retstr

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.get_switch_id() == other.get_switch_id() and
                self.get_cookie() == other.get_cookie() and
                self.get_flooding_ports() == other.get_flooding_ports() and
                self.get_intermediate_vlan() == other.get_intermediate_vlan())
        

    def get_flooding_ports(self):
        return self.flooding_ports

    def get_intermediate_vlan(self):
        return self.intermediate_vlan


