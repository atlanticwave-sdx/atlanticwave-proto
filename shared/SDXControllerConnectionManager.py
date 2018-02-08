# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project

# Commands
# SDX to LC
SDX_NEW_RULE = "NEW_RULE"
SDX_RM_RULE = "RM_RULE"

# Responses
# LC to SDX
SDX_IDENTIFY = "IDENTIFY"




# Connection details
IPADDR = '127.0.0.1'
PORT = 5555

from lib.ConnectionManager import *
from lib.Connection import Connection
from shared.SDXControllerConnectionManagerConnection import *
from shared.UserPolicy import UserPolicyBreakdown

from Queue import Queue

class SDXControllerConnectionManagerNotConnectedError(ConnectionManagerValueError):
    pass

class SDXControllerConnectionManager(ConnectionManager):
    ''' Used to manage the connection with the SDX Controller. '''

    def __init__(self):
        super(SDXControllerConnectionManager, self).__init__(
            SDXControllerConnection)
        # associations are for easy lookup of connections based on the name of
        # the Local Controller.
        
        # associations contains name:Connection pairs
        self.associations = {}

    def send_breakdown_rule_add(self, bd):
        ''' This takes in a UserPolicyBreakdown and send it to the Local
            Controller that it has a connection to in order to add rules. '''
        try:
            # Find the correct client
            lc_cxn = self._find_lc_cxn(bd)
        
            # Send rules
            for rule in bd.get_list_of_rules():
                switch_id = rule.get_switch_id()
                msg = SDXMessageInstallRule(rule, switch_id)
                lc_cxn.send_protocol(msg)

        except SDXControllerConnectionManagerNotConnectedError as e:
            # Connection doesn't yet exist. Nothing to do.
            pass
        
        except Exception as e: raise

    def send_breakdown_rule_rm(self, bd):
        ''' This takes in a UserPolicyBreakdown and send it to the Local 
            Controller that it has a connection to in order to remove rules. 
        '''
        try:
            # Find the correct client
            lc_cxn = self._find_lc_cxn(bd)

            # Send rm for each rule, slightly different than adding rules
            for rule in bd.get_list_of_rules():
                switch_id = rule.get_switch_id()
                rule_cookie = rule.get_cookie()
                msg = SDXMessageRemoveRule(rule_cookie, switch_id)
                lc_cxn.send_protocol(msg)

        except SDXControllerConnectionManagerNotConnectedError as e:
            # Connection doesn't yet exist. Nothing to do.
            pass
            
        except Exception as e: raise

    def _find_lc_cxn(self, bd):
        lc = bd.get_lc()
        lc_cxn = None
        if lc in self.associations.keys():
            lc_cxn = self.associations[lc]

        if lc_cxn == None:
            raise SDXControllerConnectionManagerNotConnectedError("%s is not in the current connections.\n    Current connections %s" % (lc, self.clients))

        return lc_cxn

    def associate_cxn_with_name(self, name, cxn):
        ''' This is to allow connections to be referred to by shortnames, rather
            than by IP addresses and whatnot. Related to the 
            send_breakdown_rule_*() functions. 
            More hacky than I'd like it to be. '''
        self.associations[name] = cxn
        #FIXME: Should this check to make sure that the cxn is in self.clients?
        # Clean up queues for the new connection.
        if name in self.non_connected_queues.keys():
            q = self.non_connected_queues[name]
            del self.non_connected_queues[name]
            while not q.empty():
                (bd, add_or_remove) = q.get()
                if add_or_remove == SDX_NEW_RULE:
                    self.send_breakdown_rule_add(bd)
                elif add_or_remove == SDX_RM_RULE:
                    self.send_breakdown_rule_rm(bd)
        

