# Copyright 2016 - Sean Donovan
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

class SDXControllerConnection(Connection):
    ''' Handles connection state machine for SDX Controller connections.
        Has a very simple protocol:
          - Message number
          - Message number ack
          - Size of Message
          - Message data
    '''

    def __init__(self):
        self.msg_num = 0
        self.msg_ack = 0

        #FIXME: There's more that needs to go on h ere
        pass

    def recv_protocol(self, data):
        # Based on Connection.recv(), but updated for the additional protocol
        # related info.
        try:
            sock_data = ''
            meta_data = ''
            while len(meta_data) < 12:
                sock_data = self.sock.recv(12-len(meta_data))
                meta_data += sock_data
                if len(meta_data) == 12:
                    (msg_num, msg_ack, recv_size) = struct.unpack('>iii',
                                                                  meta_data)[0]
            total_len = 0
            total_data = []
            if recv_size > 524388:
                recv_size = 524288
            while total_len < size:
                sock_data = self.sock.recv(recv_size)
                total_data.append(sock_data)
                total_len = sum([len(i) for i in total_data])
                recv_size = size - total_len
                if recv_size > 524388:
                    recv_size = 524288
            data_raw = ''.join(total_data)

            # Unpickle!
            data = pickle.loads(data_raw)

            # Check/update msg_num and msg_ack
            if msg_ack > self.msg_num:
                print "msg_ack from peer went backwards! %d:%d" % (msg_ack,
                                                                   self.msg_num)
            if msg_num < self.msg_ack
                print "msg_num from peer went backwards! %d:%d" % (msg_num,
                                                                   self.msg_ack)
            self.msg_ack = msg_num
            return data

    def send_protocol(self, data):
        # Based on Connection.send(), but updated for the additional protocol
        # related info.
        try:
            data_raw = pickle.dumps(data)
            self.sock.sendall(struct.pack('>iii',
                                          self.msg_num,
                                          self.msg_ack,
                                          len(data_raw)) + data_raw)
            # Update msg_num
            self.msg_num += 1
        except:
            raise


class SDXControllerConnectionManager(ConnectionManager):
    ''' Used to manage the connection with the SDX Controller. '''

    def __init__(self):
        super(SDXControllerConnectionManager, self).__init__(
            SDXControllerConnection)
        # associations are for easy lookup of connections based on the name of
        # the Local Controller.
        
        # associations contains name:Connection pairs
        self.associations = {}

        # When a message arrives for a non-connected Local Controller, rather
        # than failing the installation of the rule, queue it until the LC has
        # connected. Once connected, install rules and empty out the queue.
        
        # non_connected_queues contains name:(rule, type) queues for 
        # added/removed rules that are sent before a connection is established.
        # Entries deleted once emptied.
        self.non_connected_queues = {}

    def send_breakdown_rule_add(self, bd):
        ''' This takes in a UserPolicyBreakdown and send it to the Local
            Controller that it has a connection to in order to add rules. '''
        try:
            # Find the correct client
            lc_cxn = self._find_lc_cxn(bd)
        
            # Send rules
            for rule in bd.get_list_of_rules():
                switch_id = rule.get_switch_id()
                lc_cxn.send_cmd(SDX_NEW_RULE, (switch_id, rule))

        except SDXControllerConnectionManagerNotConnectedError as e:
            # Connection doesn't yet exist.
            self._queue_rule_for_connection(bd.get_lc(), bd, SDX_NEW_RULE)
        
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
                lc_cxn.send_cmd(SDX_RM_RULE, (switch_id, rule_cookie))

        except SDXControllerConnectionManagerNotConnectedError as e:
            # Connection doesn't yet exist.
            self._queue_rule_for_connection(bd.get_lc(), bd, SDX_RM_RULE)
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
        

    def _queue_rule_for_connection(self, name, bd, add_or_remove):
        ''' This queues a rule for a connection that doesn't yet exist. Queue 
            may not exist, so may need to create it. 
            add_or_remove is either SDX_NEW_RULE or SDX_RM_RULE, as appropriate.
        '''
        if name not in self.non_connected_queues.keys():
            #FIXME: this probably should have a max length, otherwise we could
            #get a resource exhaustion situation.
            self.non_connected_queues[name] = Queue()
        self.non_connected_queues[name].put((bd, add_or_remove))

