from __future__ import absolute_import
from __future__ import unicode_literals
# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project

# from LCRule import *

from LCRule import *

class ManagementSDXRecoverRule(LCRule):
    ''' This rule by SDX to try covering connection once LocalController
        connection is lost (heart beat is missing).
        Created by ManagementSDXRecoverPolicy. '''

    def __init__(self, switch_id):
        ''' Field descritpions:
                switch_id - Which switch is involved
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
