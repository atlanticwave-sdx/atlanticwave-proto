# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton
from AuthorizationManager import AuthorizationManager
from BreakdownEngine import BreakdownEngine
from ValidityInspector import ValidityInspector

class RuleManager(object):
    ''' The RuleManager keeps track of all rules that are installed (and their 
        metadata), the breakdowns of the abstract rule per local controller as 
        created by the BreakdownEngine, as well as orchestrating new rule 
        requests and removals.
        Workflow: The REST API will send new rules by participants who are 
        allowed to send rules (of any type), it will be sent to the 
        ValididyInspector to check if it is a valid rule, then sent to the 
        BreakdownEngine to break it into constituent parts, and finally the 
        RuleManager will check with the AuthorizationInspector to see if the 
        breakdowns are allowed to be installed by that particular user. 
        Singleton. ''' 
    __metaclass__ = Singleton

    def __init__(self):
        pass

    def add_rule(self, rule, user):
        ''' Adds a rule for a particular user. Returns rule hash if successful, 
            failure message based on why the rule installation failed. Also 
            returns the rules that are pushed to the local controller(s) for 
            review. '''
        pass

    def test_add_rule(self, rule, user):
        ''' Similar to add rule, save for actually pushing the rule to the local 
            controllers. Useful for testing out whether a rule will be added as 
            expected, or to preview what rules will be pushed to the local 
            controller(s). '''
        pass

    def remove_rule(self, rule_hash, user):
        ''' Removes the rule that corresponds to the rule_hash that wa returned 
            either from add_rule() or found with get_rules(). If user does not 
            have removal ability, returns an error. '''
        pass

    def get_rules(self, filter=None):
        ''' Used for searching for rules based on a filter. The filter could be 
            based on the rule type, the user that installed the rule, the local 
            controllers that have rules installed, or the hash_value of the rule.
            This will be useful for both administrators and for participants for
            debugging. This will return a list of tuples (rule_hash, rule). '''
        #FIXME: What other filters?
        pass

    def get_rule_details(self, rule_hash):
        ''' This will return details of a rule, including the rule itself, the 
            local controller breakdowns, the user who installed the rule, the 
            date and time of rule installation. '''
        #FIXME: What other details are useful here?
        pass
