# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


class UserRule(object):
    ''' This is the interface between the SDX controller and the user-level 
        application. This will likely be heavily modified over the course of 
        development, more so than most other interfaces. '''

    def __init__(self, username, json_rule):
        ''' Parses the json_rule passed in to populate the UserRule. '''
        self.username = username
        self.ruletype = None
        self.json_rule = json_rule
        self._parse_json(self.json_rule)

        # The breakdown list should be a list of UserRuleBreakdown objects.
        self.breakdown = None
        self.rule_hash = None
        

    @staticmethod
    def check_syntax(json_rule):
        ''' Used to validate syntax of json user rules before they are parsed.
            Must be implemented by child classes. '''
        raise NotImplementedError("Subclasses must implement this.")

    def breakdown_rule(self, topology, authorization_func):
        ''' Called by the BreakdownEngine to break a user rule apart. Should
            only be called by the BreakdownEngine, which passes the topology
            and authorization_func to it.
            Returns a UserRuleBreakdown object.
            Must be implemented by child classes. '''
        raise NotImplementedError("Subclasses must implement this.")

    def check_validity(self, topology, authorization_func):
        ''' Called by the ValidityInspector to check if the particular object is
            valid. Should only be called by the ValidityInspector, which passes
            the topology and authorization_func to it. ''' 
        raise NotImplementedError("Subclasses must implement this.")

    def set_breakdown(self, breakdown):
        self.breakdown = breakdown

    def get_breakdown(self, breakdown):
        return self.breakdown

    def set_rule_hash(self, hash):
        self.rule_hash = hash

    def get_rule_hash(self, hash):
        return self.rule_hash

    def _parse_json(self, json_rule):
        ''' Actually does parsing. 
            Must be implemented by child classes. '''
        raise NotImplementedError("Subclasses must implement this.")


        
class UserRuleBreakdown(object):
    ''' This provides a standard way of holding broken down rules. Captures the
        local controller and the rules passed to them. '''

    def __init__(self, lc, list_of_rules):
        self.lc = lc
        self.rules = list_of_rules

    def get_lc(self):
        return self.lc

    def get_list_of_rules(self):
        return list_of_rules
