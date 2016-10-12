# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import SingletonMixin
from AuthorizationInspector import AuthorizationInspector
from BreakdownEngine import BreakdownEngine
from ValidityInspector import ValidityInspector

import dataset

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

def TESTING_CALL(param):
    ''' RuleManager requires two parameters for proper initialization. However
        we also want for the REST API to be able to get a copy of the RuleManger
        easily.'''
    raise RuleManagerError("RuleManager has not been properly initialized")

class RuleManager(SingletonMixin):
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
    
    
    def __init__(self, send_user_rule_breakdown_add=TESTING_CALL,
                 send_user_rule_breakdown_remove=TESTING_CALL,
                 database=":memory:"):
        # The params are used in order to maintain import hierarchy.
        
        # Start database/dictionary
        self.db = dataset.connect('sqlite:///' + database)
        self.rule_table = self.db['rules']        # All the rules live here.
        self.config_table = self.db['config']     # Key-value configuration DB
        
        # Initialize rule counter. Used to track the rules as they are installed
        # It may be in the DB.
        rulenum = self.config_table.find_one(key='rule_number')
        if rulenum == None:
            self.rule_number = 1
            self.config_table.insert({'key':'rule_number',
                                      'value':self.rule_number})
        else:
            self.rule_number = rulenum['value']
        

        # Use these to send the rule to the Local Controller
        self.set_send_add_rule(send_user_rule_breakdown_add)
        self.set_send_rm_rule(send_user_rule_breakdown_remove)

    def set_send_add_rule(self, fcn):
        self.send_user_add_rule = fcn

    def set_send_rm_rule(self, fcn):
        self.send_user_rm_rule = fcn

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
            valid = ValidityInspector.instance().is_valid_rule(rule)
        except Exception as e:
            raise RuleManagerValidationError(
                "Rule cannot be validated, threw exception: %s, %s" %
                (rule, str(e)))
        
        if valid != True:
            raise RuleManagerValidationError(
                "Rule cannot be validated: %s" % rule)
        
        # Get the breakdown of the rule
        try:
            breakdown = BreakdownEngine.instance().get_breakdown(rule)
        except Exception as e: raise
#            raise RuleManagerBreakdownError(
#                "Rule breakdown threw exception: %s, %s" %
#                (rule, str(e)))
        if breakdown == None:
            raise RuleManagerBreakdownError(
                "Rule was not broken down: %s" % rule)

        # Check if the user is authorized to perform those actions.
        try:
            authorized = AuthorizationInspector.instance().is_authorized(rule.username, rule)
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

        self.rule_table.insert({'hash':rule.get_rule_hash(), 
                                'rule':rule})

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
            valid = ValidityInspector.instance().is_valid_rule(rule)
        except Exception as e:
            raise RuleManagerValidationError(
                "Rule cannot be validated, threw exception: %s, %s" %
                (rule, str(e)))
        
        if valid != True:
            raise RuleManagerValidationError(
                "Rule cannot be validated: %s" % rule)
        

        # Get the breakdown of the rule
        try:
            breakdown = BreakdownEngine.instance().get_breakdown(rule)
        except Exception as e:
            raise RuleManagerBreakdownError(
                "Rule breakdown threw exception: %s, %s" %
                (rule, str(e)))
        if breakdown == None:
            raise RuleManagerBreakdownError(
                "Rule was not broken down: %s" % rule)

        # Check if the user is authorized to perform those actions.
        try:
            authorized = AuthorizationInspector.instance().is_authorized(rule.username, rule)
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
        if self.rule_table.find_one(hash=rule_hash) == None:
            raise RuleManagerError("rule_hash doesn't exist: %s" % rule_hash)

        rule = self.rule_table.find_one(hash=rule_hash)['rule']
        authorized = None
        try:
            authorized = AuthorizationInspector.instance().is_authorized(user, rule) #FIXME
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


        # Remove from the rule_table
        self.rule_table.delete(hash=rule_hash)

    def remove_all_rules(self, user):
        ''' Removes all rules. Just an alias for repeatedly calling 
            remove_rule() without needing to know all the hashes. '''
        for rule in self.rule_table:
            self.remove_rule(rule['hash'], user)


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
        return self.rule_table.find_one(hash=rule_hash)

    def _get_new_rule_number(self):
        ''' Returns a new rule number for use. For now, it's incrementing by one,
            but this can be a security risk, so should be a random number/hash.
            Good for 4B (or more!) rules!
        '''
        self.rule_number += 1
        self.config_table.update({'key':'rule_number', 
                                  'value':self.rule_number})
        return self.rule_number
