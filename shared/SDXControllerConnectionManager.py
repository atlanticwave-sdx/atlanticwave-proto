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

from Queue import Queue, Empty

# Connection Queue actions defininition
NEW_CXN = "New Connection"
DEL_CXN = "Remove Connection"


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

        # Connection action queue
        self.cxn_q = Queue()
        

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

    def get_cxn_queue_element(self):
        ''' This returns a tuple (action,connection) or None if there aren't any
            cxn actions. The Action is of the list, defined up above:
               NEW_CXN
               DEL_CXN
            The connection is a SDXControllerConnectionManagerConnection that
            the action applies to.
        '''
        try:
            if self.cxn_q.empty():
                return None
            return self.cxn_q.get(False)
        except Empty as e:
            # This is raised if the cxn_q is empty of events.
            # Normal behaviour
            return None
        except:
            raise

    def add_new_cxn_to_queue(self, cxn):
        ''' Used by Connections to add themselves to the queue. '''
        self.cxn_q.put((NEW_CXN, cxn))
    
    def add_del_cxn_to_queue(self, cxn):
        ''' Used by Connections when they are closing. '''
        self.cxn_q.put((DEL_CXN, cxn))
    
    def _internal_new_connection(self, sock, address):
        ''' This is a rewrite of ConnectionManager._internal_new_connection()
            that adds some callbacks to SDXControllerConnectionManagerConnection
            to kick things to the connection queue. '''
        client_ip, client_port = address
        client_connection = self.connection_cls(client_ip, client_port, sock)
        client_connection.set_delete_callback(self.add_del_cxn_to_queue)
        client_connection.set_new_callback(self.add_new_cxn_to_queue)
        self.listening_callback(client_connection)

    def open_outbound_connection(self, ip, port):
        ''' This is a wrapper for ConnectionManager.open_outbound_connection
            that adds some callbacks to SDXControllerConnectionManagerConnection
            to kick things to the connection queue. '''
        cxn = super(SDXControllerConnectionManager,
                    self).open_outbound_connection(ip, port)
        cxn.set_delete_callback(self.add_del_cxn_to_queue)
        cxn.set_new_callback(self.add_new_cxn_to_queue)
        return cxn

