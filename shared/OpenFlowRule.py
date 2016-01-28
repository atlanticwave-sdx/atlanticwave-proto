# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


class OpenFlowRule(object):
    ''' This is passed between the Local Controller and the SDX controller. It
        is, effectively, a structure. It has a list of valid fields that it will
        accept for matches and actions and will reject anything that’s invalid
        when being created/added. '''

    def __init__(self, matches=[], actions=[], table=0, priority=100, cookie=0):
        pass

    def addMatch(match):
        ''' Adds match field(s) to the match string. 
            Can match on multiple fields simultaneously. '''
        pass

    def addAction(action):
        ''' Add action(s) to be taken on matched packets. '''
        pass

    def addCookie(cookie):
        ''' Set the unique ID for the rule. '''
        pass

    def addTable(table):
        ''' Set the table to be used for this match-action. '''
        pass

    def addPriority(priority):
        ''' Sets the OpenFlow priority field for htis match-action. '''
        pass

    def getMatch():
        pass

    def getAction():
        pass

    def getCookie():
        pass
    
    def getTable():
        pass

    def getPriority():
        pass
