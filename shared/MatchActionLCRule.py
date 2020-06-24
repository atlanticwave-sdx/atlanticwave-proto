from __future__ import absolute_import
# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from .LCRule import *
from .LCFields import *
from .LCAction import *

class MatchActionLCRule(LCRule):
    ''' This structure is used to pass Rules that create match-action rules on
        for a single location. These are close to OpenFlow rules, but abstract
        away quite of bit of the detail. ''' 

    def __init__(self, switch_id, matches, actions, ingress=True):
        ''' Field descriptions:
                matches - List of matches for a given rule (LCFields)
                actions - List of actions for a given rule (LCAction)
                ingress - Boolean describing if the rule is an ingress or egress
                    rule. 
        '''
        super(MatchActionLCRule, self).__init__(switch_id)

        # Validate inputs, as much as we can.
        if type(matches) != type([]):
            raise LCRuleTypeError("matches is not a list: %s" % type(matches))
        for match in matches:
            if not isinstance(match, LCField):
                raise LCRuleTypeError("match %s is not an LCField: %s" %
                                      (match, type(match)))

        if type(actions) != type([]):
            raise LCRuleTypeError("actions is not a list: %s" % type(actions))
        for action in actions:
            if not isinstance(action, LCAction):
                raise LCRuleTypeError("action %s is not an LCAction: %s" %
                                      (action, type(action)))

        if type(ingress) != bool:
            raise LCRuleTypeError("ingress is not a bool: %s, %s" % 
                                  (ingress, type(ingress)))

        
        # Save off inputs.
        self.matches = matches
        self.actions = actions
        self.ingress = ingress

    def __str__(self):
        retstr = ("MatchActionLCRule: switch%s:%s:%s\n    %s\n    %s" % 
                  (self.switch_id, self.cookie, self.ingress,
                   self.matches, self.actions))
        return retstr

    def get_matches(self):
        return self.matches

    def get_actions(self):
        return self.actions

    def get_ingress(self):
        return self.ingress
