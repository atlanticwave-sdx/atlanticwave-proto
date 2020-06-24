from __future__ import print_function
# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project

# Unit tests for shared.SDXControllerConnectionManagerConnection module.
import unittest
import socket
import threading
import cPickle as pickle
from time import sleep
from shared.SDXControllerConnectionManagerConnection import *
from lib.Connection import select as cxnselect

class dummy_rule(object):
    def __init__(self, name, switch_id):
        self.name = name
        self.switch_id = switch_id

    def get_switch_id(self):
        return self.switch_id
                 

def get_initial_rules_5(dummy):
    print("### Getting rules for %s" % dummy)
    return [dummy_rule('rule1', 1),
            dummy_rule('rule2', 2),
            dummy_rule('rule3', 3),
            dummy_rule('rule4', 4),
            dummy_rule('rule5', 5)]
def get_initial_rules_0(dummy):
    print("### Getting rules for %s" % dummy)
    return []
def set_name_1(dummy):
    print("### Setting name to %s" % dummy)

def new_callback(dummy):
    print("New Callback %s" % dummy)
    
def del_callback(dummy):
    print("Del Callback %s" % dummy)
    
def install_rule(rule):
    print("--- install_rule(%s)" %rule)

class SDXMessageInitTest(unittest.TestCase):
    def test_SDXMessage_init(self):
        try:
            msg = SDXMessage('dummy', ['dummy'], ['UNCONNECTED'])
        except:
            self.fail("Failed test_SDXMessage_init")
            
    def test_HeartbeatRequest_init(self):
        msg = SDXMessageHeartbeatRequest()
        json_msg = {'HBREQ':{}}
        msg2 = SDXMessageHeartbeatRequest(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)

    def test_HeartbeatResponse_init(self):
        msg = SDXMessageHeartbeatResponse()
        json_msg = {'HBRESP':{}}
        msg2 = SDXMessageHeartbeatResponse(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)

    def test_CapabilitiesRequest_init(self):
        msg = SDXMessageCapabilitiesRequest()
        json_msg = {'CAPREQ':{}}
        msg2 = SDXMessageCapabilitiesRequest(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)

    def test_CapabilitiesResponse_init(self):
        msg = SDXMessageCapabilitiesResponse('data')
        json_msg = {'CAPRESP':{'capabilities':'data'}}
        msg2 = SDXMessageCapabilitiesResponse(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)

    def test_InitialRuleCount_init(self):
        msg = SDXMessageInitialRuleCount(17)
        json_msg = {'INITRC':{'initial_rule_count':17}}
        msg2 = SDXMessageInitialRuleCount(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)

    def test_InitialRuleRequest_init(self):
        msg = SDXMessageInitialRuleRequest(12)
        json_msg = {'INITRREQ':{'rules_to_go':12}}
        msg2 = SDXMessageInitialRuleRequest(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)

    def test_InitialRulesComplete_init(self):
        msg = SDXMessageInitialRulesComplete()
        json_msg = {'INITCOMP':{}}
        msg2 = SDXMessageInitialRulesComplete(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)

    def test_TransitionToMainPhase_init(self):
        msg = SDXMessageTransitionToMainPhase()
        json_msg = {'TRANSMP':{}}
        msg2 = SDXMessageTransitionToMainPhase(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)

    def test_InstallRule_init(self):
        msg = SDXMessageInstallRule("jibberish!", 3)
        json_msg = {'INSTALL':{'rule':"jibberish!", 'switch_id':3}}
        msg2 = SDXMessageInstallRule(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)
        
    def test_InstallRuleComplete_init(self):
        msg = SDXMessageInstallRuleComplete(33)
        json_msg = {'INSTCOMP':{'cookie':33}}
        msg2 = SDXMessageInstallRuleComplete(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)

    def test_InstallRuleFailure_init(self):
        msg = SDXMessageInstallRuleFailure(33,"some error condition")
        json_msg = {'INSTFAIL':{'cookie':33,
                                'failure_reason':"some error condition"}}
        msg2 = SDXMessageInstallRuleFailure(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)

    def test_RemoveRule_init(self):
        msg = SDXMessageRemoveRule(4321, 3)
        json_msg = {'REMOVE':{'cookie':4321, 'switch_id':3}}
        msg2 = SDXMessageRemoveRule(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)
        
    def test_RemoveRuleComplete_init(self):
        msg = SDXMessageRemoveRuleComplete(33)
        json_msg = {'RMCOMP':{'cookie':33}}
        msg2 = SDXMessageRemoveRuleComplete(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)

    def test_RemoveRuleFailure_init(self):
        msg = SDXMessageRemoveRuleFailure(33,"some error condition")
        json_msg = {'RMFAIL':{'cookie':33,
                              'failure_reason':"some error condition"}}
        msg2 = SDXMessageRemoveRuleFailure(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)

    def test_UnknownSource_init(self):
        msg = SDXMessageUnknownSource("11:22:33:44:55:66", 3, "switch-a")
        json_msg = {'UNKNOWN':{'mac_address':"11:22:33:44:55:66",
                               'port':3,
                               'switch':"switch-a"}}
        msg2 = SDXMessageUnknownSource(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)

    def test_SwitchChangeCallback_init(self):
        msg = SDXMessageSwitchChangeCallback(1234,'OPAQUEDATA!')
        json_msg = {'CALLBACK':{'cookie':1234,
                                'data':"OPAQUEDATA!"}}
        msg2 = SDXMessageSwitchChangeCallback(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)


class SDXConnectionEstablishmentTest(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        self.port = 5585

        # This is for the listening socket. 
        self.ReceivingSocket = socket.socket(socket.AF_INET,
                                             socket.SOCK_STREAM)
        self.ReceivingSocket.bind((self.ip, self.port))

        #These two will be the client and server side connections.
        self.ServerCxn = None
        self.ClientCxn = None

        self.RecvThread = threading.Thread(target=self.receiving_thread)
        self.RecvThread.daemon = True
        self.RecvThread.start()
        sleep(.5)

    def tearDown(self):
        if self.ServerCxn != None:
            self.ServerCxn.close()
        if self.ClientCxn != None:
            self.ClientCxn.close()
        self.ReceivingSocket.close()

    def receiving_thread(self):
        self.ReceivingSocket.listen(1)
        
        sock, client_address = self.ReceivingSocket.accept()

        self.ServerCxn = SDXControllerConnection(self.ip, self.port,
                                                        sock, __name__)
        sleep(.5) # Waiting for connection.
        self.ServerCxn.set_new_callback(new_callback)
        self.ServerCxn.set_delete_callback(del_callback)
        self.ServerCxn.transition_to_main_phase_SDX(set_name_1,
                                                    get_initial_rules_5)
        

    def test_connection_establishment(self):
        print("Beginning connection")
        self.ClientSocket = socket.socket(socket.AF_INET,
                                          socket.SOCK_STREAM)
        self.ClientSocket.connect((self.ip, self.port))
        self.ClientCxn = SDXControllerConnection(self.ip, self.port,
                                                        self.ClientSocket, __name__)
        self.ClientCxn.set_new_callback(new_callback)
        self.ClientCxn.set_delete_callback(del_callback)
        self.ClientCxn.transition_to_main_phase_LC('TESTING', "asdfjkl;",
                                                    install_rule)
        print("pre close")
        self.ClientSocket.close()
        print("close")
                                                    

class SDXConnectionEstablishmentEmptyTest(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        self.port = 5586
        
        # This is for the listening socket. 
        self.ReceivingSocket = socket.socket(socket.AF_INET,
                                             socket.SOCK_STREAM)
        self.ReceivingSocket.bind((self.ip, self.port))

        #These two will be the client and server side connections.
        self.ServerCxn = None
        self.ClientCxn = None

        self.RecvThread = threading.Thread(target=self.receiving_thread)
        self.RecvThread.daemon = True
        self.RecvThread.start()
        sleep(.5)
        

    def tearDown(self):
        if self.ServerCxn != None:
            self.ServerCxn.close()
        if self.ClientCxn != None:
            self.ClientCxn.close()
        self.ReceivingSocket.close()

    def receiving_thread(self):
        self.ReceivingSocket.listen(1)
        
        sock, client_address = self.ReceivingSocket.accept()

        self.ServerCxn = SDXControllerConnection(self.ip, self.port,
                                                        sock, __name__)
        self.ServerCxn.set_new_callback(new_callback)
        self.ServerCxn.set_delete_callback(del_callback)
        self.ServerCxn.transition_to_main_phase_SDX(set_name_1,
                                                    get_initial_rules_0)
        

    def test_connection_establishment_empty(self):
        print("Beginning connection")
        self.ClientSocket = socket.socket(socket.AF_INET,
                                          socket.SOCK_STREAM)
        self.ClientSocket.connect((self.ip, self.port))
        self.ClientCxn = SDXControllerConnection(self.ip, self.port,
                                                        self.ClientSocket, __name__)
        self.ClientCxn.set_new_callback(new_callback)
        self.ClientCxn.set_delete_callback(del_callback)
        self.ClientCxn.transition_to_main_phase_LC('TESTING', "asdfjkl;",
                                                    install_rule)
        print("pre close")
        self.ClientSocket.close()
        print("close")


class SDXConnectionHeartbeatTest(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        self.port = 5587

        # This is for the listening socket. 
        self.ReceivingSocket = socket.socket(socket.AF_INET,
                                             socket.SOCK_STREAM)
        self.ReceivingSocket.bind((self.ip, self.port))

        #These two will be the client and server side connections.
        self.ServerCxn = None
        self.ClientCxn = None

        self.RecvThread = threading.Thread(target=self.receiving_thread)
        self.RecvThread.daemon = True
        self.RecvThread.start()
        sleep(.5)

        self.ClientSocket = socket.socket(socket.AF_INET,
                                          socket.SOCK_STREAM)
        self.ClientSocket.connect((self.ip, self.port))
        self.ClientCxn = SDXControllerConnection(self.ip, self.port,
                                                 self.ClientSocket, __name__)
        self.ClientCxn.set_new_callback(new_callback)
        self.ClientCxn.set_delete_callback(del_callback)
        self.ClientCxn.transition_to_main_phase_LC('TESTING', "qwerJ:LK",
                                                   install_rule)

    def tearDown(self):
        if self.ServerCxn != None:
            self.ServerCxn.close()
        if self.ClientCxn != None:
            self.ClientCxn.close()
        self.ReceivingSocket.close()

    def receiving_thread(self):
        self.ReceivingSocket.listen(1)
        
        sock, client_address = self.ReceivingSocket.accept()

        self.ServerCxn = SDXControllerConnection(self.ip, self.port,
                                                        sock, __name__)
        sleep(.5) # Wait for connection.
        self.ServerCxn.set_new_callback(new_callback)
        self.ServerCxn.set_delete_callback(del_callback)
        self.ServerCxn.transition_to_main_phase_SDX(set_name_1,
                                                    get_initial_rules_5)


        cxns = [self.ServerCxn, self.ClientCxn]
        while True:
            try:
                r,w,e = cxnselect(cxns, [], cxns)
            except Exception as e:
                raise

            for entry in r:
                msg = entry.recv_protocol()
                if msg != None:
                    raise Exception("Not supposted to receive anything %s:%s" %
                                    (entry, msg))
                #print "Received an empty message (Heartbeat!) %s" % hex(id(entry))
                
    def test_heartbeat(self):
        # Confirm that connections are established, get current heartbeat counts
        self.failUnlessEqual(self.ClientCxn.get_state(),  "MAIN_PHASE")
        self.failUnlessEqual(self.ServerCxn.get_state(),  "MAIN_PHASE")
        init_client_req_count = self.ClientCxn._heartbeat_request_sent
        init_client_resp_count = self.ClientCxn._heartbeat_response_sent
        init_server_req_count = self.ServerCxn._heartbeat_request_sent
        init_server_resp_count = self.ServerCxn._heartbeat_response_sent

        # 2 heartbeats + 10%
        sleep(22)
        
        # Confirm that heartbeat counts have incremented by 2
        end_client_req_count = self.ClientCxn._heartbeat_request_sent
        end_client_resp_count = self.ClientCxn._heartbeat_response_sent
        end_server_req_count = self.ServerCxn._heartbeat_request_sent
        end_server_resp_count = self.ServerCxn._heartbeat_response_sent

        self.assertGreaterEqual(end_client_req_count, init_client_req_count+2)
        self.assertGreaterEqual(end_client_resp_count, init_client_resp_count+2)
        self.assertGreaterEqual(end_server_req_count, init_server_req_count+2)
        self.assertGreaterEqual(end_server_resp_count, init_server_resp_count+2)

        
if __name__ == '__main__':
    unittest.main()
