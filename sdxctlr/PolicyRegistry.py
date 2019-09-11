# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
import os
import imp
import sys
import inspect
from glob import glob
from lib.AtlanticWaveRegistry import AtlanticWaveRegistry

class PolicyRegistryTypeError(TypeError):
    pass

class PolicyRegistry(AtlanticWaveRegistry):
    ''' The PolicyRegistry provides a centralized lookup service for converting 
        user policies into the class that implements them. 
        Singleton. '''

    def __init__(self, loggeridprefix='sdxcontroller'):
        loggerid = loggeridprefix + '.policyregistry'
        super(PolicyRegistry, self).__init__(loggerid)

        # Find where UserPolicy is defined
        for d in sys.path:
            for root, dirs, files in os.walk(d, topdown=False):
                for name in files:
                    if "UserPolicy.py" == name:
                        self.logger.warning("%s found UserPolicy: %s" %
                                            (self.__class__.__name__,
                                             os.path.join(root, name)))
                        self.policylocation = root
                        break
        
        # Initialize policy DB
        self.policytype_db = {}

        self.logger.warning("%s initialized: %s" % (self.__class__.__name__,
                                                    hex(id(self))))

    def find_policies(self):
        polpath = self.policylocation

        # Thanks to this stackoverflow thread:
        # https://stackoverflow.com/questions/3178285/list-classes-in-directory-python
        self.logger.info("%s looking for policies in %s" % (
            self.__class__.__name__, polpath))

        sys.path.append(polpath)
        import UserPolicy # so it's importing UserPolicy the say way it's importing everything from the shared directory.
                    


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
                    self.add_policytype(classvalue)

        sys.path.remove(polpath)
        self.logger.info("%s Found all policy types in %s" % (
            self.__class__.__name__, polpath))

        


    def add_policytype(self, classlink):
        ''' Adds a new policy type to the registry. '''
        name = classlink.get_policy_name()
        self.logger.info("Available Policy type: " + name)
        self.policytype_db[name] = classlink

    def get_policy_class(self, policytype):
        ''' From a policytype, get the correct class to use to implement the 
            policy.
            Raise an error if it's not in the registry. '''
        if policytype in self.policytype_db.keys():
            return self.policytype_db[policytype]
        raise PolicyRegistryTypeError(
            "policytype %s is not in the policytype_db" % policytype)

    def get_list_of_policies(self):
        ''' Returns a list of all known policy types.'''
        return self.policytype_db.keys()
