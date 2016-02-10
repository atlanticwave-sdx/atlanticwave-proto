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
        accept for matches and actions and will reject anything that’s invalid
        when being created/added. '''

    def __init__(self, matches=[], instruction=None, table=0, priority=100, cookie=0):
        ''' matches is a list of OpenFlowMatch objects.
            instruction is an OpenFlowInstruction.
            table is a table number.
            priority is a priority number.
            cookie is an arbitrary cookie number. '''

        if type(matches) != type([]):
            raise OpenFlowRuleTypeError("matches must be in a list")
        for entry in matches:
            if not isinstance(entry, OpenFlowMatch):
                raise OpenFlowRuleTypeError("matches must be a list of OpenFlowMatch objects")
        self.matches = matches

        if (instruction != None or
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

    def addMatch(match, check_validity=True):
        ''' Adds match field(s) to the match string. 
            match can be either a single Match, or a list of Matches.
            Can match on multiple fields simultaneously. '''
        single = True
        if type(match) == type([]):
            single = False
            for entry in match:
                if not isinstance(match, OpenFlowMatch):
                    raise OpenFlowTypeError("match must be an OpenFlowMatch or list of OpenFlowMatch objects")
        if not isinstance(match, OpenFlowMatch):
            raise OpenFlowTypeError("match must be an OpenFlowMatch or list of OpenFlowMatch objects")

        if check_validity:
            if single:
                match.check_validity()
            else:
                for entry in match:
                    entry.check_validity()
                    
        self.match.append(match)

    def setInstruction(instruction, check_validity=True):):
        ''' Add instruction to be taken on matched packets. '''
        if not isinstance(instruction, OpenFlowInstruction):
            raise OpenFlowTypeError("instruction must be an OpenFlowInstruction")

        if check_validity:
            instruction.check_validity()

        self.instruction = instruction


    def setCookie(cookie):
        ''' Set the unique ID for the rule. '''
        if not isinstance(cookie, int):
            raise OpenFlowTypeError("cookie must be an int")

        if cookie < OF_COOKIE_MIN or cookie > OF_COOKIE_MAX:
            raise OpenFlowRuleValueError("cookie is outside of valid range: " +
                                         str(OF_COOKIE_MIN) + "-" +
                                         str(OF_COOKIE_MAX))
        self.cookie = cookie

    def setTable(table):
        ''' Set the table to be used for this match-action. '''
        if table < OF_TABLE_MIN or table > OF_TABLE_MAX:
            raise OpenFlowRuleValueError("table is outside of valid range: " +
                                         str(OF_TABLE_MIN) + "-" +
                                         str(OF_TABLE_MAX))
        self.table = table

    def setPriority(priority):
        ''' Sets the OpenFlow priority field for htis match-action. '''
        if priority < OF_PRIORITY_MIN or table > OF_PRIORITY_MAX:
            raise OpenFlowRuleValueError("priority is outside of valid range: " +
                                         str(OF_PRIORITY_MIN) + "-" +
                                         str(OF_PRIORITY_MAX))
        self.priority = priority
        
    def getMatch():
        return self.match

    def getInstruction():
        return self.instruction

    def getCookie():
        return self.cookie
    
    def getTable():
        return self.table

    def getPriority():
        return self.priority
