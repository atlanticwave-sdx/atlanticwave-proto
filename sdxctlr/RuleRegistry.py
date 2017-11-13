# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
from lib.Singleton import SingletonMixin

class RuleRegistryTypeError(TypeError):
    pass

class RuleRegistry(SingletonMixin):
    ''' The RuleRegistry provides a centralized lookup service for converting 
        user rules into the class that implements them. 
        Singleton. '''

    def __init__(self):
        # Setup logger
        self._setup_logger()

        # Initialize rule DB
        self.ruletype_db = {}

    def _setup_logger(self):
        ''' Internal function for setting up the logger formats. '''
        # reused from https://github.com/sdonovan1985/netassay-ryu/blob/master/base/mcm.py
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        console.setFormatter(formatter)
        logfile = logging.FileHandler('sdxcontroller.log')
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(formatter)
        self.logger = logging.getLogger('sdxcontroller.rulereg')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console)
        self.logger.addHandler(logfile) 


    def add_ruletype(self, ruletype, classlink):
        ''' Adds a new rule type to the registry. ruletype is the text form of a
            rule (e.g., 'path') while classlink is a pointer to the class that
            implements the ruletype. 
            Note: multiple ruletypes could be covered by the same class (e.g., 
            NetAssay does this). '''
        self.ruletype_db[ruletype] = classlink

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
