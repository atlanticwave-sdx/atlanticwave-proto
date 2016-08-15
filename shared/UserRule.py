# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


class UserRule(object):
    ''' This is the interface between the SDX controller and the user-level 
        application. This will likely be heavily modified over the course of 
        development, more so than most other interfaces. '''

    def __init__(self, username, json_rule):
        ''' Parses the json_rule passed in to populate the UserRule. '''
        self.username = username
        self.json_rule = json_rule
        self._parse_json(self.json_rule)
        

    @staticmethod
    def check_syntax(json_rule):
        ''' Used to validate syntax of json user rules before they are parsed.
            Must be implemented by child classes. '''
        raise NotImplementedError("Subclasses must implement this.")

    def breakdown_rule(self, topology, authorization_func):
        ''' Called by the BreakdownEngine to break a user rule apart. Should
            only be called by the BreakdownEngine, which passes the topology
            and authorization_func to it.
            Must be implemented by child classes. '''
        raise NotImplementedError("Subclasses must implement this.")

    def check_validity(self, topology, authorization_func):
        ''' Called by the ValidityInspector to check if the particular object is
            valid. Should only be called by the ValidityInspector, which passes
            the topology and authorization_func to it. ''' 
        raise NotImplementedError("Subclasses must implement this.")

    def _parse_json(self, json_rule):
        ''' Actually does parsing. 
            Must be implemented by child classes. '''
        raise NotImplementedError("Subclasses must implement this.")

        
