# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton
from AuthorizationInspector import AuthorizationInspector
from BreakdownEngine import BreakdownEngine
from ValidityInspector import ValidityInspector

class RuleManagerError(Exception):
    ''' Parent class, can be used as a catch-all for other errors '''
    pass

class RuleManagerValidationError(RuleManagerError):
    ''' When a validation fails, raise this. '''
    pass

class RuleManagerBreakdownError(RuleManagerError):
    ''' When a breakdown fails, raise this. '''
    pass

class RuleManagerAuthorizationError(RuleManagerError):
    ''' When a authorization fails, raise this. '''
    pass

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

    
    
    def __init__(self, send_user_rule_breakdown_add,
                 send_user_rule_breakdown_remove):
        # The params are used in order to maintain import hierarchy.

        # Initialize rule counter. Used to track the rules as they are installed.
        self.rule_number = 1
        
        # Start database/dictionary
        self.rule_db = {}

        # Get references to helpers
        self.vi = ValidityInspector()
        self.be = BreakdownEngine()
        self.ai = AuthorizationInspector()

        # Send the rule to the Local Controller
        self.send_user_add_rule = send_user_rule_breakdown_add
        self.send_user_rm_rule = send_user_rule_breakdown_remove

    def add_rule(self, rule):
        ''' Adds a rule for a particular user. Returns rule hash if successful, 
            failure message based on why the rule installation failed. Also 
            returns a reference to the rule (e.g., a tracking number) so that 
            more details can be retrieved in the future. '''

        valid = None
        breakdown = None
        authorized = None
        # Check if valid rule
        try:
            valid = self.vi.is_valid_rule(rule)
        except Exception as e:
            raise RuleManagerValidationError(
                "Rule cannot be validated, threw exception: %s, %s" %
                (rule, str(e)))
        
        if valid != True:
            raise RuleManagerValidationError(
                "Rule cannot be validated: %s" % rule)
        
        # Get the breakdown of the rule
        try:
            breakdown = self.be.get_breakdown(rule)
        except Exception as e: raise
#            raise RuleManagerBreakdownError(
#                "Rule breakdown threw exception: %s, %s" %
#                (rule, str(e)))
        if breakdown == None:
            raise RuleManagerBreakdownError(
                "Rule was not broken down: %s" % rule)

        # Check if the user is authorized to perform those actions.
        try:
            authorized = self.ai.is_authorized(rule.username, rule)
        except Exception as e:
            raise RuleManagerAuthorizationError(
                "Rule not authorized with exception: %s, %s" %
                (rule, str(e)))
            
        if authorized != True:
            raise RuleManagerAuthorizationError(
                "Rule is not authorized: %s" % rule)

        # If everything passes, set the hash and breakdown, and put into database
        rule.set_rule_hash(self._get_new_rule_number())
        rule.set_breakdown(breakdown)
        self.rule_db[rule.get_rule_hash()] = rule

        #FIXME: Actually send add rules to LC!
        #FIXME: This should be in a try block.
        try:
            for bd in breakdown:
                self.send_user_add_rule(bd)
        except Exception as e: raise
            
        return rule.get_rule_hash()
        

    def test_add_rule(self, rule):
        ''' Similar to add rule, save for actually pushing the rule to the local 
            controllers. Useful for testing out whether a rule will be added as 
            expected, or to preview what rules will be pushed to the local 
            controller(s). '''
        
        valid = None
        breakdown = None
        authorized = None
        # Check if valid rule
        try:
            valid = self.vi.is_valid_rule(rule)
        except Exception as e:
            raise RuleManagerValidationError(
                "Rule cannot be validated, threw exception: %s, %s" %
                (rule, str(e)))
        
        if valid != True:
            raise RuleManagerValidationError(
                "Rule cannot be validated: %s" % rule)
        

        # Get the breakdown of the rule
        try:
            breakdown = self.be.get_breakdown(rule)
        except Exception as e:
            raise RuleManagerBreakdownError(
                "Rule breakdown threw exception: %s, %s" %
                (rule, str(e)))
        if breakdown == None:
            raise RuleManagerBreakdownError(
                "Rule was not broken down: %s" % rule)

        # Check if the user is authorized to perform those actions.
        try:
            authorized = self.ai.is_authorized(rule.username, rule)
        except Exception as e:
            raise RuleManagerAuthorizationError(
                "Rule not authorized with exception: %s, %s" %
                (rule, str(e)))
            
        if authorized != True:
            raise RuleManagerAuthorizationError(
                "Rule is not authorized: %s" % rule)

        
        return breakdown

    def remove_rule(self, rule_hash, user):
        ''' Removes the rule that corresponds to the rule_hash that wa returned 
            either from add_rule() or found with get_rules(). If user does not 
            have removal ability, returns an error. '''
        if rule_hash not in self.rule_db.keys():
            raise RuleManagerError("rule_hash doesn't exist: %s" % rule_hash)

        rule = self.rule_db[rule_hash]
        authorized = None
        try:
            authorized = self.ai.is_authorized(user, rule) #FIXME
        except Exception as e:
            raise RuleManagerAuthorizationError("User %s is not authorized to remove rule %s with exception %s" % (user, rule_hash, str(e)))
        if authorized != True:
            raise RuleManagerAuthorizationError("User %s is not authorized to remove rule %s" % (user, rule_hash))

        #FIXME: Actually send remove rules to LC!
        #FIXME: This should be in a try block.
        try:
            for bd in rule.breakdown:
                self.send_user_rm_rule(bd)
        except Exception as e: raise


        # Remove from the rule_db
        del self.rule_db[rule_hash]


    def get_rules(self, filter=None):
        ''' Used for searching for rules based on a filter. The filter could be 
            based on the rule type, the user that installed the rule, the local 
            controllers that have rules installed, or the hash_value of the rule.
            This will be useful for both administrators and for participants for
            debugging. This will return a list of tuples (rule_hash, rule). '''

        #FIXME: Need to define what the filters actually are.
        pass

    def get_rule_details(self, rule_hash):
        ''' This will return details of a rule, including the rule itself, the 
            local controller breakdowns, the user who installed the rule, the 
            date and time of rule installation. '''
        if rule_hash in self.rule_db.keys():
            return self.rule_db[rule_hash]
        return None

    def _get_new_rule_number(self):
        ''' Returns a new rule number for use. For now, it's incrementing by one,
            but this can be a security risk, so should be a random number/hash.
            Good for 4B (or more!) rules!
        '''
        self.rule_number += 1
        return self.rule_number
