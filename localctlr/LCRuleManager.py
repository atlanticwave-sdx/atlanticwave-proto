# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project

import cPickle as pickle
from lib.AtlanticWaveManager import AtlanticWaveManager

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
class LCRuleManagerDeletionError(LCRuleManagerError):
    pass

class LCRuleManager(AtlanticWaveManager):
    ''' This keeps track of LCRules. It provideds a database for easier 
        filtering.
        Singleton. '''

    def __init__(self, loggeridprefix='localcontroller',
                 db_filename=':memory:'):
        loggerid = loggeridprefix + '.lcrulemanager'
        super(LCRuleManager, self).__init__(loggerid)
        
        # Setup DB.
        db_tuples = [('rule_table', 'lcrules')] 
        self._initialize_db(db_filename, db_tuples)
        # Rule entry looks like:
        # {cookie_value : {'status': RULE_STATUS_ACTIVE,
        #                  'rule': rule_value}}        

        self._valid_table_columns = ['cookie','switch_id','status','rule']

        # Setup initial rules related stuff.
        self._initial_rules_list = []

        self.logger.warning("%s initialized: %s" % (self.__class__.__name__,
                                                    hex(id(self))))


    def add_rule(self, cookie, switch_id, lcrule, 
                 status=RULE_STATUS_INSTALLING):
        # Insert LC rule into db, using the cookie and switch_id as the index
        # Validate status
        if status not in VALID_RULE_STATUSES:
            raise LCRuleManagerTypeError("Status not valid: %s" % status)

        textrule = pickle.dumps(lcrule)

        # Confirm that we're not inserting a duplicate rule.
        dupes = self._find_rules({'cookie':cookie,
                                  'switch_id':switch_id})
        if dupes != None:
            for dupe in dupes:
                (c,sid,lcr,stat) = dupe
                if lcr == lcrule:
                    raise LCRuleManagerValidationError(
                        "Duplicate add_rule for %s:%s:%s" %
                        (cookie, switch_id, str(lcrule)))

        # Translate rule into a string so it can be stored
        self.rule_table.insert({'cookie':cookie,
                                'switch_id':switch_id,
                                'status':status,
                                'rule':textrule})

        listrules = self._find_rules({})
        self.logger.debug("%s - %s --- MCEVIK add_rule: listrules: %s" % (self.__class__.__name__, hex(id(self)), str(listrules)))

    def rm_rule(self, cookie, switch_id):
        # Remove LC rule identified by cookie and switch_id
        
        record = self.rule_table.find_one(cookie=cookie, switch_id=switch_id)
        if record != None:
            self.rule_table.delete(cookie=cookie, switch_id=switch_id)
        else:
            raise LCRuleManagerDeletionError(
                "Cannot delete %s:%s: doesn't exist" %
                (cookie, switch_id))

    def set_status(self, cookie, switch_id, status):
        if status not in VALID_RULE_STATUSES:
            raise LCRuleManagerValidationError(
                "Invalid Rule Status provided: %s" % status)
        # Changes the status of a particular rule
        record = self.rule_table.find_one(cookie=cookie, switch_id=switch_id)
        if record != None:
            self.rule_table.update({'cookie':cookie,
                                    'switch_id':switch_id,
                                    'status':status},
                                   ['cookie'])

    def _find_rules(self, filter={}):
        # If filter=={}, return all rules.
        # Returns a list of (cookie, switch_id, rule, status) tuples

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
                   x['switch_id'],
                   pickle.loads(str(x['rule'])),
                   x['status']) for x in results]
        return retval
        

    def get_rules(self, cookie, switch_id, full_tuple=False):
        ''' Returns a list of all rules matching cookie and switch_id. 
            Generally, there will be only one rule, but there could be multiple.
            If  full_tuple==True, then a list of tuples will be returned:
                (cookie, switch_id, rule, status)
        '''

        listrules = self._find_rules({})
        self.logger.debug("%s - %s --- MCEVIK get_rules: listrules: %s" % (self.__class__.__name__, hex(id(self)), str(listrules)))

        # Get the rule specified by cookie
        rules = self.rule_table.find(cookie=cookie, switch_id=switch_id)
        self.logger.debug("%s - %s --- MCEVIK get_rules: rules: %s" % (self.__class__.__name__, hex(id(self)), str(rules)))

        if full_tuple:
            retval = [(x['cookie'],
                       x['switch_id'],
                       pickle.loads(str(x['rule'])),
                       x['status']) for x in rules]
            self.logger.debug("%s - %s --- MCEVIK get_rules: retval full_tuple: %s" % (self.__class__.__name__, hex(id(self)), str(retval)))
            return retval

        retval = [pickle.loads(str(x['rule'])) for x in rules]
        self.logger.debug("%s - %s --- MCEVIK get_rules: retval : %s" % (self.__class__.__name__, hex(id(self)), str(retval)))
        return retval

    def add_initial_rule(self, rule, cookie, switch_id):
        # Used during initial rule stage of inialization.
        self.logger.debug(
            "Adding a new rule to the _initial_rules_list: %s:%s:%s" %
            (cookie, switch_id, rule.get_data()['rule']))
        self._initial_rules_list.append((cookie, switch_id, rule))

    def initial_rules_complete(self):
        ''' Returns two lists: rules for deletion, rules to be added. None of 
            the rules in either of these lists are added or removed from this 
            DB. This is just a service for the LC to make life a bit easier.
            NOTE: clear_initial_rules() *must* be called afterwards.
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
        
        self.logger.debug("IRC _INITIAL_RULES_LIST %s" % 
                          self._initial_rules_list)
        
        list_of_c_and_s = [(x['cookie'], x['switch_id'])
                           for x in self.rule_table.find()]
        c_and_s_from_irl = [(c,s) for (c,s,r) in self._initial_rules_list]

        for t in list_of_c_and_s:
            if t not in c_and_s_from_irl:
                (c,s) = t
                rules = self.get_rules(c,s, True)
                for rule in rules:
                    (c,s,r,t) = rule
                    delete_list.append((r,c,s))

        for t in c_and_s_from_irl:
            if t not in list_of_c_and_s:
                (c,s) = t
                for (c1,s1,r1) in self._initial_rules_list:
                    if (c==c1 and s==s1):
                        add_list.append((r1,c1,s1))

        return (delete_list, add_list)

    def clear_initial_rules(self):
        ''' Called by LC once current set of initial rules are not needed 
            anymore.
            NOTE: this *could* be done by initial_rules_complete, but it would 
            be a weird side effect that is dirty. As such, separate function. A 
            very complicated separate function.
        '''
        self.logger.debug("Clearing _initial_rules_list")
        self._initial_rules_list = []
