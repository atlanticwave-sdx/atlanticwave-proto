# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project


from LCRule import *

VLAN_MIN = 0
VLAN_MAX = 4095

class EdgePortLCRule(LCRule):
    ''' This structure is used to pass the identities of edge ports during 
        initial bootstrapping of switches.
        Created by LearnedDestinationPolicy. '''

    def __init__(self, switch_id, edgeport):
        ''' Field descriptions:
                switch_id - Which switch is involved
                edgeport - Physical port on the switch
        '''
        super(EdgePortLCRule, self).__init__(switch_id)

        # Validate inputs, as much as we can.
        if type(edgeport) != int:
            raise LCRuleTypeError("edgeport is not an int: %s, %s" % 
                                  (edgeport, type(edgeport)))
        
        # Save off inputs.
        self.edgeport = edgeport
        
    def __str__(self):
        retstr = ("EdgePortLCRule: switch %s, %s:%s" %
                  (self.switch_id, self.cookie, self.edgeport))
        return retstr

    def get_edgeport(self):
        return self.edgeport

