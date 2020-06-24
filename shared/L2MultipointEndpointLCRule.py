from __future__ import absolute_import
# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project


from .LCRule import *

VLAN_MIN = 0
VLAN_MAX = 4080

class L2MultipointEndpointLCRule(LCRule):
    ''' This structure is used to pass L2Multpoint rules for endpoint switches.
        If an endpoint exists on a switch, this LCRule will be used. If it is 
        not and endpoint and just passing traffic through, 
        L2MultipointFloodLCRule is to be used.
        Created by L2MultipointPolicy. '''

    def __init__(self, switch_id, flooding_ports, endpoint_ports_and_vlans,
                 intermediate_vlan, bandwidth):
        ''' Field descriptions:
                switch_id - Which switch is involved
                flooding_ports - List of ports connected to the endpoint switch 
                  that are not endpoint ports. Flooding-only port on the 
                  intermediate VLAN. Can be None, if endpoints are located 
                  solely on one switch. Necessary field as all the ports are 
                  potentially connected when flooding.
                endpoint_ports_and_vlans - List of tuples of endpoints and their
                  associated VLANs. For example, [(3, 1400), (6, 1200)] would be
                  Port 3 on VLAN 1400 and port 6 on VLAN 1200.
                intermediate_vlan - VLAN used for traffic between endpoint 
                  ports. Can be None, if endpoints are located solely on one 
                  switch.
                bandwidth - Amount of bandwidth (in bits per second) allowed.
                  Can be None, if no bandwidth restrictions.
        '''
        super(L2MultipointEndpointLCRule, self).__init__(switch_id)

        # Validate inputs, as much as we can.
        if not (type(flooding_ports) == None or type(flooding_ports) == list):
            raise LCRuleTypeError("flooding_ports is not None or a list: %s, %s" % 
                                  (flooding_ports, type(flooding_ports)))
        for port in flooding_ports:
            if type(port) != int:
                raise LCRuleTypeError("port in flooding_ports is not an int: %s, %s" % 
                                  (port, type(port)))
        if type(endpoint_ports_and_vlans) != list:
            raise LCRuleTypeError("endpoint_ports_and_vlans is not a list: %s, %s" % 
                                  (endpoint_ports_and_vlans,
                                   type(endpoint_ports_and_vlans)))
        for p_and_v in endpoint_ports_and_vlans:
            if type(p_and_v) != tuple:
                raise LCRuleTypeError("Port and VLAN in endpoint_ports_and_vlans is not a tuple: %s, %s" %
                                      (p_and_v, type(p_and_v)))
            if len(p_and_v) != 2:
                raise LCRuleTypeError("Port and VLAN in endpoint_ports_and_vlans is not a tuple of length 2: %s, %i" %
                                      (p_and_v, len(p_and_v)))
            (p, v) = p_and_v
            if type(p) != int:
                raise LCRuleTypeError("port in endpoint_ports_and_vlans is not an int: %s, %s" %
                                      (p, type(p)))
            if type(v) != int:
                raise LCRuleTypeError("vlan in endpoint_ports_and_vlans is not an int: %s, %s" %
                                      (v, type(v)))
            if (v < VLAN_MIN) or (v > VLAN_MAX):
                raise LCRuleTypeError("vlan in endpoint_ports_and_vlans is not in valid range (%s,%s): %s" %
                                      (VLAN_MIN, VLAN_MAX, tv))

        if type(intermediate_vlan) != int:
            raise LCRuleTypeError("intermediate_vlan is not an int: %s, %s" %
                                      (intermediate_vlan,
                                       type(intermediate_vlan)))
        
        if not (type(bandwidth) == type(None) or type(bandwidth) == int):
            raise LCRuleTypeError("bandwidth is not None or an int: %s, %s" %
                                      (bandwidth, type(bandwidth)))
                
        # Save off inputs.
        self.flooding_ports = flooding_ports
        self.endpoint_ports_and_vlans = endpoint_ports_and_vlans
        self.intermediate_vlan = intermediate_vlan
        self.bandwidth = bandwidth
        
    def __str__(self):
        retstr = ("L2MultipointEndpointLCRule: switch %s, %s:(%s), (%s), %s, %s" %
                  (self.switch_id, self.cookie, self.flooding_ports,
                   self.endpoint_ports_and_vlans, self.intermediate_vlan,
                   self.bandwidth))
        return retstr

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.get_switch_id() == other.get_switch_id() and
                self.get_cookie() == other.get_cookie() and
                self.get_flooding_ports() == other.get_flooding_ports() and
                self.get_endpoint_ports_and_vlans() == other.get_endpoint_ports_and_vlans() and
                self.get_intermediate_vlan() == other.get_intermediate_vlan() and
                self.get_bandwidth() == other.get_bandwidth())            
                

    def get_flooding_ports(self):
        return self.flooding_ports

    def get_endpoint_ports_and_vlans(self):
        return self.endpoint_ports_and_vlans

    def get_intermediate_vlan(self):
        return self.intermediate_vlan

    def get_bandwidth(self):
        return self.bandwidth


