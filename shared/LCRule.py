# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


class LCRuleTypeError(TypeError):
    pass

class LCRuleValueError(ValueError):
    pass

class LCRule(object):
    ''' Parent class for all Local Controller-SDX Controller rules. '''

    def __init__(self, switch_id, cookie=None):
        ''' Field descriptions:
                switch_id - Switch ID of the switch. This is context dependent:
                    OpenFlow uses one format, P4 uses something else, Cisco 
                    can use something else.
                cookie - Unique identifier for the given rule. Opaque, just 
                    used for identification. Smaller is better, a number is 
                    probably best, but a string could work. For instance: 
                        "sdonovan-756"
                    could be the user 'sdonovan' 756th rule.
        ''' 
        self.switch_id = switch_id
        self.cookie = cookie

    def get_switch_id(self):
        return self.switch_id

    def get_cookie(self):
        return self.cookie

    def set_cookie(self, cookie):
        # used by the RuleManager for internal tracking.
        self.cookie = cookie
