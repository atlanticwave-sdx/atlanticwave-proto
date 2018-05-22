# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project

from LCRule import *

MANAGEMENT_VLAN_MIN = 4080
MANAGEMENT_VLAN_MAX = 4089
class ManagementVLANLCRule(LCRule):
    ''' This structure is used at each switch that the Management VLAN traverses
        to define the physical ports that the VLAN will traverse. Traffic 
        forwarding will be handled exclusively through MAC learning in this 
        itteration, much like how L2Multipoint is handled. '''

    def __init__(self, switch_id, mgmt_vlan, mgmt_vlan_ports):
        ''' Field descriptions:
                switch_id - The switch involved
                mgmt_vlan - VLAN ID of Managment VLAN
                mgmt_vlan_ports - List of ports connected on the Management 
                  VLAN. 
        '''
        super(IBMBootstrappingLCRule, self).__init__(switch_id)

        # Validate inputs
        if type(mgmt_vlan) != int:
            raise LCRuleTypeError("mgmt_vlan is not an int: %s, %s" %
                                  (mgmt_vlan, type(mgmt_vlan)))
        if ((mgmt_vlan < MANAGEMENT_VLAN_MIN) or
            (mgmt_vlan > MANAGEMENT_VLAN_MAX)):
            raise LCRuleValueError("mgmt_vlan is not in valid range (%s,%s): %s",
                                   (MANAGEMENT_VLAN_MIN,
                                    MANAGEMENT_VLAN_MAX,
                                    mgmt_vlan))
            
        if type(mgmt_vlan_ports) != list:
            raise LCRuleTypeError("mgmt_vlan_ports is not a list: %s, %s" %
                                  (mgmt_vlan_ports, type(mgmt_vlan_ports)))

        for p in mgmt_vlan_ports:
            if type(p) != int:
                raise LCRuleTypeError("port in mgmt_vlan_ports is not an int: %s, %s" %
                                      (p, type(p)))
            
        # Save off inputs
        self.mgmt_vlan = mgmt_vlan
        self.mgmt_vlan_ports = mgmt_vlan_ports

    def __str__(self):
        retstr = ("ManagementVLANLCRule: switch %s: %s, %s" %
                  (self.switch_id, self.mgmt_vlan, self.mgmt_vlan_ports))
        return retstr

    def get_mgmt_vlan(self):
        return self.mgmt_vlan

    def get_mgmt_vlan_ports(self):
        return self.mgmt_vlan_ports
