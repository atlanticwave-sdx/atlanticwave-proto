# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
import os
import imp
import sys
import inspect
from glob import glob
from lib.AtlanticWaveRegistry import AtlanticWaveRegistry

class RuleRegistryTypeError(TypeError):
    pass

class RuleRegistry(AtlanticWaveRegistry):
    ''' The RuleRegistry provides a centralized lookup service for converting 
        user rules into the class that implements them. 
        Singleton. '''

    def __init__(self, loggeridprefix='sdxcontroller',
                 policylocation='../shared'):
        loggerid = loggeridprefix + '.ruleregistry'
        super(RuleRegistry, self).__init__(loggerid)

        self.policylocation = policylocation
        
        # Initialize rule DB
        self.ruletype_db = {}

        self.logger.warning("%s initialized: %s" % (self.__class__.__name__,
                                                    hex(id(self))))

    def find_policies(self, policylocation=None):
        if policylocation == None:
            policylocation = self.policylocation

        polpath = None
        if ".." in policylocation:
            polpath = os.path.dirname(os.path.relpath(policylocation))#, __file__))
        else:
            polpath = os.path.abspath(policylocation)

        polpath = policylocation
        sys.path.append(polpath)
        import UserPolicy # so it's importing UserPolicy the say way it's importing everything from the shared directory.
                    

        # Thanks to this stackoverflow thread:
        # https://stackoverflow.com/questions/3178285/list-classes-in-directory-python
        self.logger.info("%s looking for policies in %s" % (
            self.__class__.__name__, polpath))


        for file in glob(os.path.join(polpath, "*.py")):
            modulename = os.path.splitext(os.path.basename(file))[0]
            module = __import__(modulename)

            #print "\n\n\nmodule: %s" % modulename
            
            for classname in dir(module):
                classvalue = getattr(module, classname)

                # We only want local items, only want classes, and only want
                # subclasses of UserPolicy
                if ((modulename in str(classvalue)) and 
                    inspect.isclass(classvalue) and
                    issubclass(classvalue, UserPolicy.UserPolicy)):
                    #print "  %s" % classvalue
                    self.add_ruletype(classvalue)

        sys.path.remove(polpath)
        self.logger.info("%s Found all policy types in %s" % (
            self.__class__.__name__, polpath))

        


    def add_ruletype(self, classlink):
        ''' Adds a new rule type to the registry. '''
        name = classlink.get_policy_name()
        self.logger.info("Available Policy type: " + name)
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
