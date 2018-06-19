# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
from lib.AtlanticWaveRegistry import AtlanticWaveRegistry

class RuleRegistryTypeError(TypeError):
    pass

class RuleRegistry(AtlanticWaveRegistry)
    ''' The RuleRegistry provides a centralized lookup service for converting 
        user rules into the class that implements them. 
        Singleton. '''

    def __init__(self, logfilename, loggeridprefix='sdxcontroller',
                 debuglogfilename=None):
        loggerid = loggeridprefix + '.ruleregistry'
        super(RuleRegistry, self).__init__(loggerid, logfilename,
                                           debuglogfilename)

        # Initialize rule DB
        self.ruletype_db = {}

        self.logger.warning("%s initialized: %s" % (self.__class__.__name__,
                                                    hex(id(self))))

    def add_ruletype(self, classlink):
        ''' Adds a new rule type to the registry. '''
        name = classlink.get_policy_name()
        print "Available Policy type: " + name
        self.ruletype_db[name] = classlink

    def get_rule_class(self, ruletype):
        ''' From a ruletype, get the correct class to use to implement the rule.
            Raise an error if it's not in the registry. '''
        if ruletype in self.ruletype_db.keys():
            return self.ruletype_db[ruletype]
        raise RuleRegistryTypeError("Ruletype %s is not in the ruletype_db" %
                                    ruletype)

    def get_list_of_policies(self):
        ''' Returns a list of all know Policy types.'''
        return self.ruletype_db.keys()
