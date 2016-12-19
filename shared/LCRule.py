# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


class LCRuleTypeError(TypeError):
    pass

class LCRuleValueError(ValueError):
    pass

class LCRule(object):
    ''' Parent class for all Local Controller-SDX Controller rules. '''

    def __init__(self, switch_id, cookie):
        # Validate input is correct type:
        if type(cookie) != int:
            raise LCRuleTypeError("cookie is not an int: %s, %s" % 
                                  (cookie, type(cookie)))
        
        self.switch_id = switch_id
        self.cookie = cookie

    def get_switch_id(self):
        return self.switch_id

    def get_cookie(self):
        return self.cookie
