# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project

from LCRule import *

# Some noteson the current implementation:
# - This version is a first pass at implementing the Management VLAN. There are
#   a number of features that are skipped or implemented differently.
#   - This version, like other parts of the controller, is not resillient in
#     the face of failures. That is, a link failure may take down the
#     management VLAN if that link was integral to the Management VLAN spanning
#     tree.
#   - Spanning Tree is necessary to avoid cycles. Cycles are *bad*. 
#   - The Spanning Tree that is used is manually configured in the manifest.
#   - All messages are flooded
# - Future changes that are necessary:
#   - Implement localized Spanning Tree Protocol for Management VLAN
#     - This need not be 802.1 STP, but we need to be able to distributedly
#       build a spanning tree.
#   - When Spanning Tree is rebuilt due to failure, Updates to the rules are
#     needed
#   - Flooding should be updated to be learned. This probably will need to be
#     internal to the LC.
#   - This would require certain updates to the RyuTranslateInterface to handle
#     all this new functionality.
#     - Learning
#     - Connect/disconnect

###MANAGEMENT_VLAN_MIN = 4080
###MANAGEMENT_VLAN_MAX = 4089
MANAGEMENT_VLAN_MIN = 3001
MANAGEMENT_VLAN_MAX = 3006
class ManagementVLANLCRule(LCRule):
    ''' This structure is used at each switch that the Management VLAN traverses
        to define the physical ports that the VLAN will traverse. Traffic 
        forwarding will be handled exclusively through MAC learning in this 
        itteration, much like how L2Multipoint is handled. '''

    def __init__(self, switch_id, mgmt_vlan, mgmt_vlan_ports,
                 untagged_mgmt_vlan_ports=[]):
        ''' Field descriptions:
                switch_id - The switch involved
                mgmt_vlan - VLAN ID of Managment VLAN
                mgmt_vlan_ports - List of ports connected on the Management 
                  VLAN. 
                untagged_mgmt_vlan_ports - List of untagged port connected to
                  the Management VLAN. All untagged traffic on these ports is
                  tagged on ingress and untagged on egress.
        '''
        super(ManagementVLANLCRule, self).__init__(switch_id)

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

        if type(untagged_mgmt_vlan_ports) != list:
            raise LCRuleTypeError(
                "untagged_mgmt_vlan_ports is not a list: %s, %s" %
                (untagged_mgmt_vlan_ports, type(untagged_mgmt_vlan_ports)))

        for p in untagged_mgmt_vlan_ports:
            if type(p) != int:
                raise LCRuleTypeError(
                    "port in untagged_mgmt_vlan_ports is not an int: %s, %s" %
                    (p, type(p)))
        # Save off inputs
        self.mgmt_vlan = mgmt_vlan
        self.mgmt_vlan_ports = mgmt_vlan_ports
        self.untagged_mgmt_vlan_ports = untagged_mgmt_vlan_ports

    def __str__(self):
        retstr = ("ManagementVLANLCRule: switch %s, %s: %s, (%s), (%s)" %
                  (self.switch_id, self.cookie, self.mgmt_vlan,
                   self.mgmt_vlan_ports, self.untagged_mgmt_vlan_ports))
        return retstr

    def get_mgmt_vlan(self):
        return self.mgmt_vlan

    def get_mgmt_vlan_ports(self):
        return self.mgmt_vlan_ports

    def get_untagged_mgmt_vlan_ports(self):
        return self.untagged_mgmt_vlan_ports
    
