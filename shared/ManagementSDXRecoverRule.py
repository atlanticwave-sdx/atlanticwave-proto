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

# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project

from LCRule import *

class ManagementSDXRecoverRule(LCRule):
    ''' This structure is used to pass the ports that belong to a spanning tree
        to the Local Controller for handling broadcast flooding without cycles.
        Created by FloodTreePolicy. '''

    def __init__(self, switch_id):
        ''' Field descritpions:
                switch_id - Which switch is involved
                ports - List of ports that are part of the spanning tree needed
                  for broadcast flooding.
        '''
        self.switch_id = switch_id
        super(ManagementSDXRecoverRule, self).__init__(switch_id)


    def __str__(self):
        retstr = ("ManagementSDXRecoverRule: switch %s" %
                  (self.switch_id))
        return retstr

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.get_switch_id() == other.get_switch_id())

    def get_switch_id(self):
        return self.switch_id

    def get_cookie(self):
        return self.cookie
