from __future__ import absolute_import
from __future__ import unicode_literals
# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project

from .LCRule import *

class ManagementLCRecoverRule(LCRule):
    ''' This structure is used to pass the Management VLAN recover rule to 
        RyuTranslateInterface. This rule is created just for trigger recovery. '''

    def __init__(self, cookie, switch_id):
        ''' Field descritpions:
                switch_id - Which switch is involved
        '''
        super(ManagementLCRecoverRule, self).__init__(self, switch_id)
        self.cookie = cookie
        self.switch_id = switch_id

    def __str__(self):
        retstr = ("ManagementLCRecoverRule: switch %s" %
                  (self.switch_id))
        return retstr

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.get_switch_id() == other.get_switch_id())
    
    def get_switch_id(self):
        return self.switch_id

    def get_cookie(self):
        return self.cookie
