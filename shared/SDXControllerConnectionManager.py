# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project

# Commands
SDX_NEW_RULE = "NEW_RULE"
SDX_RM_RULE = "RM_RULE"



# Responses




# Connection details
IPADDR = '127.0.0.1'
PORT = 5555

from shared.ConnectionManager import *
from shared.Connection import Connection
from shared.UserPolicy import UserPolicyBreakdown

class SDXControllerConnectionManager(ConnectionManager):
    ''' Used to manage the connection with the SDX Controller. '''

    def __init__(self, *args, **kwargs):
        super(SDXControllerConnectionManager, self).__init__(*args, **kwargs)
        self.associations = {}

    def send_breakdown_rule_add(self, bd):
        ''' This takes in a UserPolicyBreakdown and send it to the Local
            Controller that it has a connection to in order to add rules. '''
        try:
            self._send_breakdown_rule(bd, SDX_NEW_RULE)
        except Exception as e: raise

    def send_breakdown_rule_rm(self, bd):
        ''' This takes in a UserPolicyBreakdown and send it to the Local 
            Controller that it has a connection to in order to remove rules. '''
        try:
            self._send_breakdown_rule(bd, SDX_RM_RULE)
        except Exception as e: raise


    def _send_breakdown_rule(self, bd, cmd):
        ''' Used by the callback functions (below) to actually perform the 
            sending of commands to the Local Controllers. This is all pretty
            much the same, with only the command changing. '''
        # The cmd is from the list of commands in  SDXControllerConnectionManager
        # Find the correct client
        lc = bd.get_lc()
        lc_cxn = None
        if lc in self.associations.keys():
            lc_cxn = self.associations[lc]    

        if lc_cxn == None:
            raise ConnectionManagerValueError("%s is not in the current connections.\n    Current connections %s" % (lc, self.clients))
        
        # Send rules
        for rule in bd.get_list_of_rules():
            lc_cxn.send_cmd(cmd, rule)

    def associate_cxn_with_name(self, name, cxn):
        ''' This is to allow connections to be referred to by shortnames, rather
            than by IP addresses and whatnot. Related to the 
            send_breakdown_rule_*() functions. 
            More hacky than I'd like it to be. '''
        self.associations[name] = cxn
        #FIXME: Should this check to make sure that the cxn is in self.clients?
                                
