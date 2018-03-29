# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project


import dataset

# List of rule statuses
RULE_STATUS_ACTIVE       = 1
RULE_STATUS_DELETING     = 2
RULE_STATUS_INSTALLING   = 3
RULE_STATUS_REMOVED      = 4

VALID_RULE_STATUSES = [RULE_STATUS_ACTIVE,
                       RULE_STATUS_DELETING,
                       RULE_STATUS_INSTALLING,
                       RULE_STATUS_REMOVED]


class LCRuleManagerError(Exception):
    pass
class LCRuleManagerTypeError(TypeError):
    pass
class LCRuleManagerValidationError(LCRuleManagerError):
    pass

class LCRuleManager(SingletonMixin):
    ''' This keeps track of LCRules. It provideds a database for easier 
        filtering.
        Singleton. '''

    def __init__(self, db_filename=':memory:'):
        # Setup logger
        self._setup_logger()
        
        # Setup DB.
        self._initialize_db(db_filename)

        self._valid_table_columns = ['cookie','status','rule']

        # Setup initial rules related stuff.
        self._initial_rules_dict = {}
        
    def _initialize_db(self, db_filename):
        # Details on the setup:
        # https://dataset.readthedocs.io/en/latest/api.html
        # https://github.com/g2p/bedup/issues/38#issuecomment-43703630
        self.logger.critical("Connection to DB: %s" % db)
        self.db = dataset.connect('sqlite:///' + db, 
                                  engine_kwargs={'connect_args':
                                                 {'check_same_thread':False}})

        #Try loading the tables, if they don't exist, create them.
        try:
            self.logger.info("Trying to load rule_table from DB")
            self.rule_table = self.db.load_table('lcrules')
        except:
            # If load_table() fails, that's fine! It means that the rule_table
            # doesn't yet exist. So, create it.
            self.logger.info("Failed to load rule_tale from DB, creating new table")
            # Rule entry looks like:
            # {cookie_value : {'status': RULE_STATUS_ACTIVE,
            #                  'rule': rule_value}}
            self.rule_table = self.db['rules']

    def _setup_logger(self):
        ''' Internal function for setting up the logger formats. '''
        # This is from LocalController
        # reused from https://github.com/sdonovan1985/netassay-ryu/blob/master/base/mcm.py
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        console.setFormatter(formatter)
        logfile = logging.FileHandler('localcontroller.log')
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(formatter)
        self.logger = logging.getLogger('localcontroller.lcrulemanager')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console)
        self.logger.addHandler(logfile)
        
    def add_rule(self, cookie, lcrule, status=RULE_STATUS_INSTALLING)
        # Insert LC rule into db, using the cookie as an index
        self.rule_table.insert({'cookie':cookie,
                                'status':status,
                                'rule':lcrule})

    def rm_rule(self, cookie):
        # Remove LC rule identified by cookie
        record = self.rule_table.find_one(cookie=cookie)
        if record != None:
            self.rule_table.delete(cookie=cookie)

    def set_status(self, cookie, status):
        if status not in VALID_RULE_STATUSES:
            raise LCRuleManagerValidationError(
                "Invalid Rule Status provided: %s" % status)
        # Changes the status of a particular rule
        record = self.rule_table.find_one(cookie=cookie)
        if record != None:
            self.rule_table.update({'cookie':cookie,
                                    'status':status},
                                   ['cookie'])

    def find_rules(self, filter={}):
        # If filter=={}, return all rules.
        # Returns a list of (cookie, rule, status) tuples

        # Validate the filter
        if filter != None:
            if type(filter) != dict:
                raise LCRuleManagerTypeError("filter is not a dictionary: %s" %
                                             type(filter))
            for key in filter.keys():
                if key not in self._valid_table_columns:
                    raise LCRuleManagerValidationError(
                        "filter column '%s' is not a valid filtering field %s" %
                        (key, self._valid_table_columns))

        # Do the search on the table. 
        results = self.rule_table.find(**filter)

        # Send Back results.
        retval = [(x['cookie'],
                   x['rule'],
                   x['status']) for x in results]
        return retval
        

    def get_rule(self, cookie):
        # Get the rule specified by cookie
        rule_entry = self.rule_table.find_one(cookie=index)
        if rule_entry != None:
            return rule_entry['rule']
        return None

    def add_initial_rule(self, rule, cookie):
        # Used during initial rule stage of inialization.
        self.logger.debug("Adding a new rule to the _initial_rules_dict: %s" %
                          cookie)
        self._initial_rules_dict[cookie] = rule

    def initial_rules_complete(self):
        ''' Returns two lists: rules for deletion, rules to be added. None of 
            the rules in either of these lists are added or removed from this 
            DB. This is just a service for the LC to make life a bit easier.
        '''
        delete_list = []
        add_list = []

        # Build up the delete_list:
        # Go through all installed rules. If it's not in the
        # _initial_rules_list, add to delete list.
        # Anything left over in the _initial_rules_list is now the add_list
        # Empty the _initial_rules_list for the next reconnection.
        # NOTE: _initial_rules_list is a list of SDXMessageInstallRules
        self.logger.debug("IRC RULE_TABLE %s" % self.rule_table)
        self.logger.debug("IRC _INITIAL_RULES_DICT %s\n\n\n" % 
                          self._initial_rules_dict)
        list_of_cookies = [x['cookie'] for x in table.find()]
        
        for index in list_of_cookies:
            if index not in self._initial_rules_dict.keys():
                rule = self.rule_table.find_one(cookie=index)['rule']
                delete_list.append(rule)

        for index in self._initial_rules_dict.keys():
            if index not in list_of_cookies:
                rule = self._initial_rules_dict[index]
                add_list.append(rule)

        return (delete_list, add_list)

    def clear_initial_rules(self):
        ''' Called by LC once current set of initial rules are not needed 
            anymore.
            NOTE: this *could* be done by initial_rules_complete, but it would 
            be a weird side effect that is dirty. As such, separate function. A 
            very complicated separate function.
        '''
        self.logger.debug("Clearning _initial_rules_dict")
        self._initial_rules_dict = {}
