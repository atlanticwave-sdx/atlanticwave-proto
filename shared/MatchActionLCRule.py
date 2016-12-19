# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from LCRule import *
from LCFields import *
from LCAction import *

class MatchActionLCRule(LCRule):
    ''' This structure is used to pass Rules that create match-action rules on
        for a single location. These are close to OpenFlow rules, but abstract
        away quite of bit of the detail. ''' 

    def __init__(self, cookie, switch_id, matches, actions, ingress=True):
        ''' Field descriptions:
                cookie - Unique identifier for the given rule. Opaque, just used
                    for identification. Smaller is better, a number is probably
                    best, but a string could work. For instance: 
                        "sdonovan-756"
                    could be the user 'sdonovan' 756th rule.
                matches - List of matches for a given rule
                actions - List of actions for a given rule
                ingress - Boolean describing if the rule is an ingress or egress
                    rule. 
        '''
        super(MatchActionLCRule, self).__init__(switch_id, cookie)

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

        if type(ingress) != type(True):
            raise LCRuleTypeError("ingress is not a bool: %s, %s" % 
                                  (ingress, type(ingress)))

        
        # Save off inputs.
        self.matches = matches
        self.actions = actions
        self.ingress = ingress
        

    def get_matches(self):
        return self.matches

    def get_actions(self):
        return self.actions

    def get_ingress(self):
        return self.ingress
