# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project


from lib.Connection import Connection
import cPickle as pickle
import struct
import threading
import socket
from time import sleep


# This list of state machien states is primarily a point of reference.
STATE_MACHINE_STAGES = [ 'UNCONNECTED',
                         'INITIALIZING',
                         'CAPABILITIES',
                         'INITIAL_RULES',
                         'INITIAL_RULES_COMPLETE',
                         'MAIN_PHASE' ]
class SDXMessageValueError(ValueError):
    pass

class SDXMessageTypeError(TypeError):
    pass

class SDXMessageConnectionFailure(EnvironmentError):
    pass

class SDXMessage(object):
    ''' Used to simplfy sending/receiving messages between SDX Controller and 
        Local Controllers. '''
    def __init__(self, name, data_json_name, validity,
                 data=None, data_json=None):
        ''' name is the name of the message class.
            validity is a list of state machine stages that are valid
            data_json_name is a list of keys for 
            data is 
              - Data can be None, expecially if it's being parsed and pulled 
                from json
        '''
        self.name = name
        self.data_json_name = data_json_name
        for entry in validity:
            if entry not in STATE_MACHINE_STAGES:
                raise SDXMessageValueError("%s is not in STATE_MACHINE_STAGES: %s" % (entry, validity))
        self.validity = validity
        if data_json != None:
            self.parse_json(data_json)
        else:
            self.data = data

    def __str__(self):
        return "%s: %s-%s-%s" % (self.name, self.validity,
                                 self.data_json_name, self.data)

    def __eq__(self, other):
        if other == None:
            return False
        return (type(self) == type(other) and
                (self.name == other.name) and
                (self.validity == other.validity) and
                (self.data_json_name == other.data_json_name) and
                (self.data == other.data))

    def get_json(self):
        json_msg = {self.name:self.data}
        return json_msg

    def parse_json(self, json_msg):
        if self.name not in json_msg.keys():
            raise SDXMessageValueError("%s is not in %s: %s" % (self.name,
                                                self.__class__.__name__,
                                                json_msg))

        if json_msg[self.name] != None:
            for entry in json_msg[self.name].keys():
                if entry not in self.data_json_name:
                    raise SDXMessageValueError("%s is not in %s: %s" % (entry,
                                                self.data_json_name,
                                                json_msg))
        # Subtle, but to make it consistent.
        if json_msg[self.name] == {}:
            self.data = None
        else:
            self.data = json_msg[self.name]

    def get_data(self):
        ''' Returns data dictionary. '''
        return self.data
    
class SDXMessageHello(SDXMessage):
    ''' Initial message sent by LC to SDX
        Only valid during initialization
        Contains name of LC '''
    def __init__(self, lcname=None, json_msg=None):
        data_json_name = ['name']
        data = {'name':lcname}
        validity = ['INITIALIZING']

        if json_msg != None:
            super(SDXMessageHello, self).__init__('HELLO',
                                                  data_json_name,
                                                  validity,
                                                  data_json=json_msg)
        else:
            super(SDXMessageHello, self).__init__('HELLO',
                                                  data_json_name,
                                                  validity,
                                                  data)

class SDXMessageHeartbeatRequest(SDXMessage):
    ''' Request heartbeat message
        Valid during main phase
        Contains no data '''
    def __init__(self, json_msg=None):
        data_json_name = None
        data = None
        validity = ['MAIN_PHASE']
        if json_msg != None:
            super(SDXMessageHeartbeatRequest, self).__init__('HBREQ',
                                                         data_json_name,
                                                         validity,
                                                         data_json=json_msg)
        else:
            super(SDXMessageHeartbeatRequest, self).__init__('HBREQ',
                                                         data_json_name,
                                                         validity,
                                                         data)
        
class SDXMessageHeartbeatResponse(SDXMessage):
    ''' Response to heartbeat message
        Valid during main phase
        Contains no data '''
    def __init__(self, json_msg=None):
        data_json_name = None
        data = None
        validity = ['MAIN_PHASE']
        if json_msg != None:
            super(SDXMessageHeartbeatResponse, self).__init__('HBRESP',
                                                        data_json_name,
                                                        validity,
                                                        data_json=json_msg)
        else:
            super(SDXMessageHeartbeatResponse, self).__init__('HBRESP',
                                                        data_json_name,
                                                        validity,
                                                        data)

class SDXMessageCapabilitiesRequest(SDXMessage):
    ''' Request from SDX controller for LC's capabilities
        Valid during capabilities
        Contains no data '''
    def __init__(self, json_msg=None):
        data_json_name = None
        data = None
        validity = ['CAPABILITIES']
        if json_msg != None:
            super(SDXMessageCapabilitiesRequest, self).__init__('CAPREQ',
                                                        data_json_name,
                                                        validity,
                                                        data_json=json_msg)
        else:
            super(SDXMessageCapabilitiesRequest, self).__init__('CAPREQ',
                                                                data_json_name,
                                                                validity,
                                                                data)

class SDXMessageCapabilitiesResponse(SDXMessage):
    ''' Response from LC to SDX with capabilities
        Valid during capabilities
        Contains a list of different capibilities. '''
    #FIXME: What are the capabilities? For initial case, we're not going to have
    #any capibilities
    def __init__(self, capabilities=None, json_msg=None):
        data_json_name = ['capabilities']
        data = {'capabilities':capabilities}
        validity = ['CAPABILITIES']
        if json_msg != None:
            super(SDXMessageCapabilitiesResponse, self).__init__('CAPRESP',
                                                        data_json_name,
                                                        validity,
                                                        data_json=json_msg)
        else:
            super(SDXMessageCapabilitiesResponse, self).__init__('CAPRESP',
                                                             data_json_name,
                                                             validity,
                                                             data)

class SDXMessageInitialRuleCount(SDXMessage):
    ''' SDX informing LC of number of ruels to install upon startup. 
        Valid during Initial Rule phase
        Contains the number of rules. '''
    def __init__(self, initial_rule_count=None, json_msg=None):
        data_json_name = ['initial_rule_count']
        data = {'initial_rule_count':initial_rule_count}
        validity = ['INITIAL_RULES']
        if json_msg != None:
            super(SDXMessageInitialRuleCount, self).__init__('INITRC',
                                                             data_json_name,
                                                             validity,
                                                             data_json=json_msg)
        else:
            super(SDXMessageInitialRuleCount, self).__init__('INITRC',
                                                             data_json_name,
                                                             validity,
                                                             data)
        
class SDXMessageInitialRuleRequest(SDXMessage):
    ''' Request from th e LC to SDX to get the next initial rule.
        Valid during Initial Rule phase
        Contains the number of rules left to request (primiarly for diagnostics)
    '''
    def __init__(self, rules_to_go=None, json_msg=None):
        data_json_name = ['rules_to_go']
        data = {'rules_to_go':rules_to_go}
        validity = ['INITIAL_RULES']
        if json_msg != None:
            super(SDXMessageInitialRuleRequest, self).__init__('INITRREQ',
                                                        data_json_name,
                                                        validity,
                                                        data_json=json_msg)
        else:
            super(SDXMessageInitialRuleRequest, self).__init__('INITRREQ',
                                                        data_json_name,
                                                        validity,
                                                        data)


class SDXMessageInitialRulesComplete(SDXMessage):
    ''' Notification from LC that it doesn't expect any more initial rules.
        Valid during Initial Rule phase
        Contains no data.
    '''
    def __init__(self, json_msg=None):
        data_json_name = None
        data = None
        validity = ['INITIAL_RULES']
        if json_msg != None:
            super(SDXMessageInitialRulesComplete, self).__init__('INITCOMP',
                                                             data_json_name,
                                                             validity,
                                                             data_json=json_msg)
        else:
            super(SDXMessageInitialRulesComplete, self).__init__('INITCOMP',
                                                             data_json_name,
                                                             validity,
                                                             data)

class SDXMessageTransitionToMainPhase(SDXMessage):
    ''' Notification from SDX to LC to move to Main Phase
        Valid during Initial Rules Complete
        Contains no data.
    '''
    def __init__(self, json_msg=None):
        data_json_name = None
        data = None
        validity = ['INITIAL_RULES_COMPLETE']
        if json_msg != None:
            super(SDXMessageTransitionToMainPhase, self).__init__('TRANSMP',
                                                            data_json_name,
                                                            validity,
                                                            data_json=json_msg)
        else:
            super(SDXMessageTransitionToMainPhase, self).__init__('TRANSMP',
                                                            data_json_name,
                                                            validity,
                                                            data)
class SDXMessageInstallRule(SDXMessage):
    ''' SDX sending a rule to an LC
        Valid during Initial Rules and Main Phase
        Contains a rule
    '''
    def __init__(self, rule=None, switch_id=None, json_msg=None):
        data_json_name = ['rule', 'switch_id']
        data = {'rule':rule, 'switch_id':switch_id}
        validity = ['INITIAL_RULES', 'MAIN_PHASE']
        if json_msg != None:
            super(SDXMessageInstallRule, self).__init__('INSTALL',
                                                        data_json_name,
                                                        validity,
                                                        data_json=json_msg)
        else:
            super(SDXMessageInstallRule, self).__init__('INSTALL',
                                                        data_json_name,
                                                        validity,
                                                        data)

class SDXMessageInstallRuleComplete(SDXMessage):
    ''' LC sends this back to SDX on successfully install a rule.
        Valid during Main Phase only
        Contains a reference to the rule
    '''
    def __init__(self, cookie=None, json_msg=None):
        data_json_name = ['cookie']
        data = {'cookie':cookie}
        validity = ['MAIN_PHASE']
        if json_msg != None:
            super(SDXMessageInstallRuleComplete, self).__init__('INSTCOMP',
                                                        data_json_name,
                                                        validity,
                                                        data_json=json_msg)
        else:
            super(SDXMessageInstallRuleComplete, self).__init__('INSTCOMP',
                                                        data_json_name,
                                                        validity,
                                                        data)

class SDXMessageInstallRuleFailure(SDXMessage):
    ''' LC sends this back to SDX on fails to install a rule.
        Valid during Main Phase only
        Contains a reference to the rule, and a failure reason
    '''
    #FIXME: What are failure reasons?
    def __init__(self, cookie=None, failure_reason=None, json_msg=None):
        data_json_name = ['cookie','failure_reason']
        data = {'cookie':cookie,
                'failure_reason':failure_reason}
        validity = ['MAIN_PHASE']
        if json_msg != None:
            super(SDXMessageInstallRuleFailure, self).__init__('INSTFAIL',
                                                        data_json_name,
                                                        validity,
                                                        data_json=json_msg)
        else:
            super(SDXMessageInstallRuleFailure, self).__init__('INSTFAIL',
                                                        data_json_name,
                                                        validity,
                                                        data)
class SDXMessageRemoveRule(SDXMessage):
    ''' SDX removing a rule to an LC
        Valid during Main Phase only
        Contains a rule
    '''
    def __init__(self, cookie=None, switch_id=None, json_msg=None):
        data_json_name = ['cookie', 'switch_id']
        data = {'cookie':cookie, 'switch_id':switch_id}
        validity = ['INITIAL_RULES', 'MAIN_PHASE']
        if json_msg != None:
            super(SDXMessageRemoveRule, self).__init__('REMOVE',
                                                       data_json_name,
                                                       validity,
                                                       data_json=json_msg)
        else:
            super(SDXMessageRemoveRule, self).__init__('REMOVE',
                                                       data_json_name,
                                                       validity,
                                                       data)

class SDXMessageRemoveRuleComplete(SDXMessage):
    ''' LC sends this back to SDX on successfully removed a rule.
        Valid during Main Phase only
        Contains a reference to the rule
    '''
    def __init__(self, cookie=None, json_msg=None):
        data_json_name = ['cookie']
        data = {'cookie':cookie}
        validity = ['MAIN_PHASE']
        if json_msg != None:
            super(SDXMessageRemoveRuleComplete, self).__init__('RMCOMP',
                                                        data_json_name,
                                                        validity,
                                                        data_json=json_msg)
        else:
            super(SDXMessageRemoveRuleComplete, self).__init__('RMCOMP',
                                                        data_json_name,
                                                        validity,
                                                        data)

class SDXMessageRemoveRuleFailure(SDXMessage):
    ''' LC sends this back to SDX on fails to remove a rule.
        Valid during Main Phase only
        Contains a reference to the rule, and a failure reason
    '''
    #FIXME: What are failure reasons?
    def __init__(self, cookie=None, failure_reason=None, json_msg=None):
        data_json_name = ['cookie','failure_reason']
        data = {'cookie':cookie,
                'failure_reason':failure_reason}
        validity = ['MAIN_PHASE']
        if json_msg != None:
            super(SDXMessageRemoveRuleFailure, self).__init__('RMFAIL',
                                                        data_json_name,
                                                        validity,
                                                        data_json=json_msg)
        else:
            super(SDXMessageRemoveRuleFailure, self).__init__('RMFAIL',
                                                        data_json_name,
                                                        validity,
                                                        data)

class SDXMessageUnknownSource(SDXMessage):
    ''' LC sends this back when a new MAC address is seen on a port. Used for 
        learning.
        Valid during Main Phase only
        Receives a port, MAC address, and switch.
    '''
    #FIXME: What are failure reasons?
    def __init__(self, mac_address=None, port=None, switch=None,
                 json_msg=None):
        data_json_name = ['mac_address', 'port', 'switch']
        data = {'mac_address':mac_address,
                'port':port,
                'switch':switch}
        validity = ['MAIN_PHASE']
        if json_msg != None:
            super(SDXMessageUnknownSource, self).__init__('UNKNOWN',
                                                          data_json_name,
                                                          validity,
                                                          data_json=json_msg)
        else:
            super(SDXMessageUnknownSource, self).__init__('UNKNOWN',
                                                          data_json_name,
                                                          validity,
                                                          data)

class SDXMessageSwitchChangeCallback(SDXMessage):
    ''' LC sends this back when there's a switch change event that a rule has
        registered a callback for within the SDX Controller. Sends back a cookie
        (from the policy - for lookup) and an opaque data structure that's 
        specific to the particular policy.
        Used by:
          - L2MultipointPolicy
        Valid during Main Phase only
        Receives a cookie and opaque data.
    '''
    #FIXME: What are failure reasons?
    def __init__(self, cookie=None, data=None, json_msg=None):
        data_json_name = ['cookie', 'data']
        data = {'cookie':cookie,
                'data':data}
        validity = ['MAIN_PHASE']
        if json_msg != None:
            super(SDXMessageSwitchChangeCallback, self).__init__(
                'CALLBACK',
                data_json_name,
                validity,
                data_json=json_msg)
        else:
            super(SDXMessageSwitchChangeCallback, self).__init__(
                'CALLBACK',
                data_json_name,
                validity,
                data)
            
SDX_MESSAGE_NAME_TO_CLASS = {'HELLO': SDXMessageHello,
                             'HBREQ': SDXMessageHeartbeatRequest,
                             'HBRESP': SDXMessageHeartbeatResponse,
                             'CAPREQ': SDXMessageCapabilitiesRequest,
                             'CAPRESP': SDXMessageCapabilitiesResponse,
                             'INITRC': SDXMessageInitialRuleCount,
                             'INITRREQ': SDXMessageInitialRuleRequest,
                             'INITCOMP': SDXMessageInitialRulesComplete,
                             'TRANSMP': SDXMessageTransitionToMainPhase,
                             'INSTALL': SDXMessageInstallRule,
                             'INSTCOMP': SDXMessageInstallRuleComplete,
                             'INSTFAIL': SDXMessageInstallRuleFailure,
                             'REMOVE' : SDXMessageRemoveRule,
                             'RMCOMP': SDXMessageRemoveRuleComplete,
                             'RMFAIL': SDXMessageRemoveRuleFailure,
                             'UNKNOWN': SDXMessageUnknownSource,
                             'CALLBACK': SDXMessageSwitchChangeCallback,
                             }

class SDXControllerConnectionValueError(ValueError):
    pass

class SDXControllerConnectionTypeError(TypeError):
    pass


class SDXControllerConnection(Connection):
    ''' Handles connection state machine for SDX Controller connections.
        Has a very simple protocol:
          - Message number
          - Message number ack
          - Size of Message
          - Message data
    '''

    def __init__(self, address, port, sock, loggerid):
        self.msg_num = 0
        self.msg_ack = 0

        #FIXME: 
        self.connection_state = 'UNCONNECTED'
        self.name = None
        self.capabilites = None

        # Heartbeat tracking
        self.outstanding_hb = False
        self.hb_thread = None
        self.heartbeat_sleep_time = 10
        self._heartbeat_request_sent = 0
        self._heartbeat_response_sent = 0

        # Callbacks
        self._del_callback = None
        self._new_callback = None

        super(SDXControllerConnection, self).__init__(address, port, sock, loggerid)

    def get_state(self):
        return self.connection_state

    def get_name(self):
        return self.name

    def set_delete_callback(self, cb):
        self._del_callback = cb

    def set_new_callback(self, cb):
        self._new_callback = cb
    
    def recv_protocol(self):
        ''' Based on Connection.recv(), but updated for the additional protocol
            related info.
            Returns a SDXMessage of the correct type or None if the message was
            a heartbeat
        '''
        
        #print "%s recv_protocol: Begin" % (threading.current_thread().ident)

        # If the socket is closed unexpectedly, it's possible the socket just
        # disappears. Annoying. Very annoying.
        if self.sock == None:
            self.close()
            self._del_callback(self)
            raise SDXMessageConnectionFailure("sock == None - %s" % self)
            
        try:
            sock_data = ''
            meta_data = ''
            meta_tries = 0
            while (len(meta_data) < 12 and
                   meta_tries < 10):
                sock_data = self.sock.recv(12-len(meta_data))
                meta_data += sock_data
                if len(meta_data) == 12:
                    (msg_num, msg_ack, size) = struct.unpack('>iii',
                                                                  meta_data)
                meta_tries += 1
            # So we don't just keep spinning when there's actually nothing there
            if meta_tries == 10:
                return None
            total_len = 0
            total_data = []
            recv_size = size
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
            if msg_num < self.msg_ack:
                print "msg_num from peer went backwards! %d:%d" % (msg_num,
                                                                   self.msg_ack)
            self.msg_ack = msg_num

            # Make the correct SDXMessage out of it.
            if len(data.keys()) != 1:
                raise SDXMessageValueError("There were multiple keys in the received data: %s" % data.keys())
            msgtype = data.keys()[0]
            msg = SDX_MESSAGE_NAME_TO_CLASS[msgtype](json_msg=data)

            # These are handy logs when needing to look at *everything*
            #print ">>>> RECEIVED %s" % msg
            #print ">>>>     JSON %s\n\n" % msg.get_json()

            # If it's a heartbeat request/heartbeat_response, send to heartbeat
            # handler and return None

            #print "%s recv_protocol: %s %s" % (
            #    threading.current_thread().ident,
            #    self.connection_state, msg)

            if type(msg) == SDXMessageHeartbeatRequest:
                self._heartbeat_request_handler(msg)
                return None
            elif type(msg) == SDXMessageHeartbeatResponse:
                self._heartbeat_response_handler(msg)
                return None

            #FIXME: Checking of rule validity
            return msg
        
        except socket.error as e:
            print "SOCKET ERROR BLOCK %s ON CXN %s" % (e.errno, self)
            if (e.errno == 104 or  # Connection reset by peer 
                e.errno == 9 or    # Bad File Descriptor
                e.errno == 32):    # Broken Pipe
                self.close()
                self._del_callback(self)
                raise SDXMessageConnectionFailure("Connection reset by peer - %s"
                                                  % self)
            elif (e.errno == 11):  # Resource temporarily unavailable
                # Not great, but happens. 
                sleep(.001)
                print "errno 11!"
            else:
                raise
        except AttributeError as e:
            print "ATTRIBUTE ERROR %s ON CXN %s" % (e, self)
            self.close()
            self._del_callback(self)
            raise SDXMessageConnectionFailure("Connection == None - %s"
                                                  % self)
            
        except:
            raise

    def send_protocol(self, sdx_message):
        # Based on Connection.send(), but updated for the additional protocol
        # related info.
        #print "%s send_protocol: %s %s" % (threading.current_thread().ident,
        #                                self.connection_state, sdx_message)
        
        # If the socket is closed unexpectedly, it's possible the socket just
        # disappears. Annoying. Very annoying.
        if self.sock == None:
            self.close()
            self._del_callback(self)
            raise SDXMessageConnectionFailure("sock == None - %s" % self)

        data = sdx_message.get_json()
        try:
            # These are handy logs when needing to look at *everything*
            #print ">>>> SENDING %s" % sdx_message
            #print ">>>>    JSON %s\n\n" % sdx_message.get_json()
            data_raw = pickle.dumps(data)
            self.sock.sendall(struct.pack('>iii',
                                          self.msg_num,
                                          self.msg_ack,
                                          len(data_raw)) + data_raw)
            # Update msg_num
            self.msg_num += 1

        except socket.error as e:
            if (e.errno == 104 or  # Connection reset by peer 
                e.errno == 9 or    # Bad File Descriptor
                e.errno == 32):    # Broken Pipe
                self.close()
                self._del_callback(self)
                raise SDXMessageConnectionFailure("Connection reset by peer %d - %s"
                                                  % (e.errno, self))
            else:
                raise
        except AttributeError as e:
            self.close()
            self._del_callback(self)
            raise SDXMessageConnectionFailure("Connection == None - %s"
                                                  % self)
            
        except:
            raise

    def transition_to_main_phase_LC(self, name, capabilities,
                                    install_rule_callback,
                                    initial_rules_complete_callback=None):
        #FIXME: These messages should check state.
        # Transition to Initializing
        self.logger.debug("%s - %s - Initializing" % (id(self), self.connection_state))
        self.connection_state = 'INITIALIZING'
        self.name = name
        self.capabilities = capabilities
                
        
        # Send hello with name, transition to Capabilities
        hello = SDXMessageHello(self.name)
        self.send_protocol(hello)
        self.logger.debug("%s - %s - Sent HELLO message, transition to CAPABILITIES" % (
            id(self), self.connection_state))
        self.connection_state = 'CAPABILITIES'

        # Wait for Request Capabilities
        reqcap = self.recv_protocol()
        if not isinstance(reqcap, SDXMessageCapabilitiesRequest):
            raise SDXControllerConnectionTypeError("SDXMessageCapabilitesRequest not received: %s, %s" % (type(reqcap), reqcap))
        self.logger.debug("%s - %s - Received Request Capabilities" % (
            id(self), self.connection_state))

        # Send Capabilities, transition to Initial Rules
        #FIXME: DOESN'T EXIST RIGHT NOW. Don't need to fill it out
        respcap = SDXMessageCapabilitiesResponse()
        self.send_protocol(respcap)
        self.logger.debug("%s - %s - Sent Capabilities, transition to INITIAL_RULES" % (
            id(self), self.connection_state))
        self.connection_state = 'INITIAL_RULES'

        # Wait for Initial Rule count
        irc = self.recv_protocol()
        if not isinstance(irc, SDXMessageInitialRuleCount):
            raise SDXControllerConnectionTypeError("SDXMessageInitialRuleCount not received: %s, %s" % (type(irc), irc))

        rule_count_left = irc.get_data()['initial_rule_count']
        self.logger.debug("%s - %s - Received Initial Rules Count %s" % (
            id(self), self.connection_state, rule_count_left))

        # Loop through initial rules:
        # - Request rule
        # - Receive rule
        # - Send rule to install_rule_callback
        while rule_count_left > 0:
            req = SDXMessageInitialRuleRequest(rule_count_left)
            self.send_protocol(req)

            rule = self.recv_protocol()
            if not isinstance(rule, SDXMessageInstallRule):
                raise SDXControllerConnectionTypeError("SDXMessageInstallRule not received: %s, %s" % (type(rule), rule))

            #FIXME: should this be the rule?
            #Should it be the contents of the rule?
            #Should it be something else? Let's leave this in for now.
            install_rule_callback(rule)

            rule_count_left -= 1
            self.logger.debug("%s - %s - Received an initial rule, Initial Rules to go %s" % (
                id(self), self.connection_state, rule_count_left))

        # Send Initial Rules Complete, Transition to Initial Rules Complete
        irc = SDXMessageInitialRulesComplete()
        self.send_protocol(irc)
        if initial_rules_complete_callback != None:
            initial_rules_complete_callback()
        self.logger.debug(
            "%s - %s - Sent Initial Rules Complete, Transitioning to INITIAL_RULES_COMPLETE" %
            (id(self), self.connection_state))
        self.connection_state = 'INITIAL_RULES_COMPLETE'

        # Wait for Transition to main phase
        tmp = self.recv_protocol()
        if not isinstance(tmp, SDXMessageTransitionToMainPhase):
            raise SDXControllerConnectionTypeError("SDXMessageTransitionToMainPhase not received: %s, %s" % (type(tmp), tmp))
        self.logger.debug("%s - %s - Received Transition message, transitioning to MAIN_PHASE" % (
            id(self), self.connection_state))

        # Transition to main phase and start the heartbeat thread
        self.connection_state = 'MAIN_PHASE'
        self.hb_thread = threading.Thread(target=_LC_heartbeat_thread,
                                          args=(self,))
        self.hb_thread.daemon = True
        self.logger.debug("%s - %s - Starting heartbeat thread, going to MAIN_PHASE" % (
            id(self), self.connection_state))
        print("%s Starting heartbeat thread LC" % 
              (threading.current_thread().ident))
        self.hb_thread.start()

        # Add connection!
        self._new_callback(self)
        self.sock.setblocking(0)

    def transition_to_main_phase_SDX(self, set_name_callback,
                                     get_initial_rule_callback):
        # Transition to Initializing
        self.logger.debug("%s - %s - Initializing" % (id(self), self.connection_state))
        self.connection_state = 'INITIALIZING'

        # Wait for hello with name, call the get_initial_rule_callback with name
        hello = self.recv_protocol()
        if not isinstance(hello, SDXMessageHello):
            raise SDXControllerConnectionTypeError("SDXMessageHello not received: %s, %s" % (type(hello), hello))
        self.logger.debug("%s - %s - Received HELLO message, Transitioning to CAPABILITIES" % (
            id(self), self.connection_state))
        
        self.name = hello.get_data()['name']
        set_name_callback(self.name)
        initial_rules = get_initial_rule_callback(self.name)

        # Transition to Capabilities, send request capabilities
        self.connection_state = 'CAPABILITIES'
        reqcap = SDXMessageCapabilitiesRequest()
        self.send_protocol(reqcap)
        self.logger.debug("%s - %s - Sent request capabilities" % (
            id(self), self.connection_state))

        # Wait for capabilities
        #FIXME: NOTHING REALLY TO DO WITH THIS YET.
        respcap = self.recv_protocol()
        if not isinstance(respcap, SDXMessageCapabilitiesResponse):
            raise SDXControllerConnectionTypeError("SDXMessageCapabilitiesResponse not received: %s, %s" % (type(respcap), respcap))
        self.logger.debug("%s - %s - Received capabilities, transitioning to INITIAL_RULES" % (
            id(self), self.connection_state))

        # Transition to Initial Rules, send Initial Rule count
        self.connection_state = 'INITIAL_RULES'
        irc = SDXMessageInitialRuleCount(len(initial_rules))
        self.send_protocol(irc)
        self.logger.debug("%s - %s - Sent Initial Rule Count, count %s" % (
            id(self), self.connection_state, len(initial_rules)))
        
        # Loop thorugh initial rules:
        # - Wait for request rule or Initial Rules Complete
        # - Send rule
        # - Remove rule from initial rule list
        # Initial Rules Complete should only be received when initial rule list
        # is empty.
        while True:
            msg = self.recv_protocol()
            if isinstance(msg, SDXMessageInitialRuleRequest):
                # Send a rule
                r = initial_rules[0]
                rule = SDXMessageInstallRule(r, r.get_switch_id())
                self.send_protocol(rule)
                self.logger.debug(
                    "%s - %s - InitialRuleRequest received, sending next initial rule" % (
                    id(self), self.connection_state))

                # Remove that rule form the initial rule list
                initial_rules = initial_rules[1:]
            elif isinstance(msg, SDXMessageInitialRulesComplete):
                # Confirm that we don't have any more rules, then bail out of
                # loop
                self.logger.debug(
                    "%s - %s - InitialRuleComplete received, Confirming all rules sent" % (
                    id(self), self.connection_state))
                if len(initial_rules) != 0:
                    raise SDXControllerConnectionValueError("initial_rules is not empty (%d: %s) but received InititialRulesComplete" % (len(initial_rules), initial_rules))
                break
            else:
                # This is an error! Protocol violation. 
                # Need to raise an exception
                raise SDXControllerConnectionTypeError("Expecting InitialRUleRequest or InitialRulesComplete, received %s: %s" % 
                                          (type(msg), str(msg)))

        self.logger.debug("%s - %s - Initial Rules are Complete" % (
                    id(self), self.connection_state))
        # Send Transition to Main Phase, transition to main phase, start
        # heartbeat thread
        tmp = SDXMessageTransitionToMainPhase()
        self.send_protocol(tmp)
        self.logger.debug("%s - %s - Sent transition to MAIN_PHASE" % (
                    id(self), self.connection_state))

        self.connection_state = 'MAIN_PHASE'
        self.hb_thread = threading.Thread(target=_SDX_heartbeat_thread,
                                          args=(self,))
        
        self.hb_thread.daemon = True
        self.logger.debug("%s - %s - Starting heartbeat thread, going to MAIN_PHASE" % (
            id(self), self.connection_state))
        print("%s Starting heartbeat thread SDX" % 
              (threading.current_thread().ident))
        self.hb_thread.start()

        # Add connection!
        self._new_callback(self)
        self.sock.setblocking(0)

    def _heartbeat_response_handler(self, hbresp):
        ''' Handles incoming HeartbeatResponses. '''
        print("%s hb_response_handler: %s" % 
              (threading.current_thread().ident, hbresp))
        if not self.outstanding_hb:
            raise SDXControllerConnectionValueError("There is no oustanding heartbeat request for this connection %s" % self)
        self.outstanding_hb = False

    def _heartbeat_request_handler(self, hbreq):
        ''' Handles incoming HeartbeatRequests. '''
        print "%s hb_request_handler: %s" % (threading.current_thread().ident,
                                             hbreq)
        resp = SDXMessageHeartbeatResponse()
        self.send_protocol(resp)
        self._heartbeat_response_sent += 1


def _SDX_heartbeat_thread(inst):
    ''' Handles automatically sending Heartbeats consistently. '''
    # Get set up
    
    # Loop
    while(True):
        # Check to see if there's an outstanding HB - there shouldn't be
        try:
            if inst.outstanding_hb == True:
                print "SDX Closing: Missing a heartbeat on %s" % hex(id(inst))
                raise SDXMessageConnectionFailure("SDX Missing heartbeat on %s" % 
                                                  hex(id(inst)))
            # Send a heartbeat request over
            req = SDXMessageHeartbeatRequest()
            inst.outstanding_hb = True
            #print "SDX Send HBREQ"
            inst.send_protocol(req)
            inst._heartbeat_request_sent += 1
        
            # Sleep
            sleep(inst.heartbeat_sleep_time)
        except:
            # Need to signal that the cxn is closed.
            print "SDX Heartbeat Closing due to error on %s" % hex(id(inst))
            inst.close()
            inst._del_callback(inst)
            return
        
def _LC_heartbeat_thread(inst):
    ''' Handles automatically sending Heartbeats consistently. '''
    # Get set up
    
    # Loop
    while(True):
        # Check to see if there's an outstanding HB - there shouldn't be
        try:
            if inst.outstanding_hb == True:
                print "LC Closing: Missing a heartbeat on %s" % hex(id(inst))
                raise SDXMessageConnectionFailure("LC Missing heartbeat on %s" % 
                                                  hex(id(inst)))
            # Send a heartbeat request over
            req = SDXMessageHeartbeatRequest()
            inst.outstanding_hb = True
            #print "LC Send HBREQ"
            inst.send_protocol(req)
            inst._heartbeat_request_sent += 1
        
            # Sleep
            sleep(inst.heartbeat_sleep_time)
        except:
            # Need to signal that the cxn is closed.
            print "LC Heartbeat Closing due to error on %s" % hex(id(inst))
            inst.close()
            inst._del_callback(inst)
            return
