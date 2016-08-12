# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton

class RuleRegistry(object):
    ''' The RuleRegistry is, in effect, a callback repository. Outside libraries
        that create participant-level rules are able to register callbacks here 
        that the ValidityInspector, the BreakdownEngine, and the REST API can use
        to perform their actions. This allows for a standardized interface that 
        outside developers can use to create new types of rules. 
        Singleton. '''
    __metaclass__ = Singleton

    class RuleRecord(object):
        ''' This is used for the current database. '''
        def __init__(self, ruletype, callback_for_syntax_check,
                     callback_for_validity, callback_for_breakdown):
            self.ruletype = ruletype
            self.callback_for_syntax_check = callback_for_syntax_check
            self.callback_for_validity = callback_for_validity
            self.callback_for_breakdown = callback_for_breakdown):

    def __init__(self):
        # Setup logger
        self._setup_logger()

        # Initialize rule DB
        self.ruletype_db = {}

        # Initialize the callback lists
        self.validation_callback_list = []
        self.breakdown_callback_list = []

    
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

    def register_rule_type(self, ruletype, callback_for_syntax_check,
                           callback_for_validity, callback_for_breakdown):
        ''' This registers a new type of rule, along with all the functions used
            for validation and breakdown.
            - ruletype is a string.
            - callback_for_syntax_check passes the whole rule for a syntax check 
              (i.e., if the rule requires a port number, this makes sure there is
              a port number as one of the fields).
            - callback_for_validity checks the rule against the topology and if
              the participant is allowed to perform a particular action (e.g., 
              can write rules for a particular port).
            - callback_for_breakdown is used to breakdown a rule into smaller, 
              per-local-controller pieces for implementation. '''
        new_rule = RuleRecord(ruletype, callback_for_syntax_check,
                              callback_for_validity, callback_for_breakdown)
        self.ruletype_db[ruletype] = new_rule

        # Send the functions to all the callbacks (validation and breakdown)
        for vcb in self.validation_callback_list:
            vcb((ruletype, callback_for_validity))
        for bcb in self.breakdown_callback_list:
            bcb((ruletype, callback_for_breakdown))        

    def syntax_check(self, rule):
        ''' Used by the REST API to perform a syntax check on a particular rule.
            To do this, it looks at its registered callbacks for a particular 
            type of rule. Returns true if syntax is valid, false otherwise. '''
        #FIXME: what does a rule look like?
        #FIXME: what does the format of the syntax check function look like?
        # Extract the ruletype

        # Get the correct RuleRecord

        # Check for syntax
        
        pass
        
    def get_validation_functions(self):
        ''' Get a list of all registered validation functions. Each entry in the
            list will be a tuple (ruletype, function). '''
        funcs = []

        for ruletype in self.ruletype_db.keys():
            funcs.append((ruletype,
                          self.ruletype_db[ruletype].callback_for_validity))
        return funcs


    def register_for_validation_functions(self, callback):
        ''' Get new validation functions as they come in. callback will take a
            tuple (ruletype, function). '''
        self.validation_callback_list.append(callback)

    def get_breakdown_functions(self):
        ''' Get a list of all breakdown functions. Each entry in the list will be
            a tuple (ruletype, function). '''
        for ruletype in self.ruletype_db.keys():
            funcs.append((ruletype,
                          self.ruletype_db[ruletype].callback_for_breakdown))
        return funcs

    def register_for_breakdown_functions(self, callback):
        ''' Get new breakdown functions as they come in. callback will take a
            tuple (ruletype, function). '''
        self.breakdown_callback_list.append(callback)


