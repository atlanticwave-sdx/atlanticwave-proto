# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project

from shared.ofconstants import *
from shared.match import *
from shared.instruction import *

class OpenFlowRuleTypeError(TypeError):
    pass

class OpenFlowRuleValueError(ValueError):
    pass

    
class OpenFlowRule(object):
    ''' This is passed between the Local Controller and the SDX controller. It
        is, effectively, a structure. It has a list of valid fields that it will
        accept for matches and actions and will reject anything that's invalid
        when being created/added. '''

    def __init__(self, match=None, instruction=None, table=0, priority=100, cookie=0):
        ''' match is an OpenFlowMatch object.
            instruction is an OpenFlowInstruction object.
            table is a table number.
            priority is a priority number.
            cookie is an arbitrary cookie number. '''

        if (instruction != None and
            not isinstance(match, OpenFlowMatch)):
            raise OpenFlowRuleTypeError("match must be an OpenFlowMatch object")
        self.match = match

        if (instruction != None and
            not isinstance(instruction, OpenFlowInstruction)):
            raise OpenFlowRuleTypeError("matches must be an OpenFlowInstruction object")
        self.instruction = instruction

        if table < OF_TABLE_MIN or table > OF_TABLE_MAX:
            raise OpenFlowRuleValueError("table is outside of valid range: " +
                                         str(OF_TABLE_MIN) + "-" +
                                         str(OF_TABLE_MAX))
        self.table = table

        if priority < OF_PRIORITY_MIN or table > OF_PRIORITY_MAX:
            raise OpenFlowRuleValueError("priority is outside of valid range: " +
                                         str(OF_PRIORITY_MIN) + "-" +
                                         str(OF_PRIORITY_MAX))
        self.priority = priority

        if cookie < OF_COOKIE_MIN or cookie > OF_COOKIE_MAX:
            raise OpenFlowRuleValueError("cookie is outside of valid range: " +
                                         str(OF_COOKIE_MIN) + "-" +
                                         str(OF_COOKIE_MAX))
        self.cookie = cookie

    def setMatch(self, match, check_validity=True):
        ''' Sets the match fields. '''

        if not isinstance(match, OpenFlowMatch):
            raise OpenFlowRuleTypeError("match must be an OpenFlowMatch object")

        if check_validity:
            match.check_validity()
                    
        self.match = match

    def setInstruction(self, instruction, check_validity=True):
        ''' Add instruction to be taken on matched packets. '''
        if not isinstance(instruction, OpenFlowInstruction):
            raise OpenFlowRuleTypeError("instruction must be an OpenFlowInstruction")

        if check_validity:
            instruction.check_validity()

        self.instruction = instruction


    def setCookie(self, cookie):
        ''' Set the unique ID for the rule. '''
        if not isinstance(cookie, int):
            raise OpenFlowRuleTypeError("cookie must be an int")

        if cookie < OF_COOKIE_MIN or cookie > OF_COOKIE_MAX:
            raise OpenFlowRuleValueError("cookie is outside of valid range: " +
                                         str(OF_COOKIE_MIN) + "-" +
                                         str(OF_COOKIE_MAX))
        self.cookie = cookie

    def setTable(self, table):
        ''' Set the table to be used for this match-action. '''
        if not isinstance(table, int):
            raise OpenFlowRuleTypeError("table must be an int")

        if table < OF_TABLE_MIN or table > OF_TABLE_MAX:
            raise OpenFlowRuleValueError("table is outside of valid range: " +
                                         str(OF_TABLE_MIN) + "-" +
                                         str(OF_TABLE_MAX))
        self.table = table

    def setPriority(self, priority):
        ''' Sets the OpenFlow priority field for htis match-action. '''
        if not isinstance(priority, int):
            raise OpenFlowRuleTypeError("priority must be an int")

        if priority < OF_PRIORITY_MIN or priority > OF_PRIORITY_MAX:
            raise OpenFlowRuleValueError("priority is outside of valid range: " +
                                         str(OF_PRIORITY_MIN) + "-" +
                                         str(OF_PRIORITY_MAX))
        self.priority = priority
        
    def getMatch(self):
        return self.match

    def getInstruction(self):
        return self.instruction

    def getCookie(self):
        return self.cookie
    
    def getTable(self):
        return self.table

    def getPriority(self):
        return self.priority
