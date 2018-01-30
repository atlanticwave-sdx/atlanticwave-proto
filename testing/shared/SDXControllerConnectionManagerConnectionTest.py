# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project

# Unit tests for shared.SDXControllerConnectionManagerConnection module.
import unittest
import socket
import threading
import cPickle as pickle
from time import sleep
from shared.SDXControllerConnectionManagerConnection import *

def get_initial_rules_5(dummy):
    print "### Getting rules for %s" % dummy
    return ['rule1',
            'rule2',
            'rule3',
            'rule4',
            'rule5']
def get_initial_rules_0(dummy):
    print "### Getting rules for %s" % dummy
    return []

def install_rule(rule):
    print "--- install_rule(%s)" %rule

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
        msg = SDXMessageInstallRule("jibberish!")
        json_msg = {'INSTALL':{'rule':"jibberish!"}}
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

    def test_UnknownSource_init(self):
        msg = SDXMessageUnknownSource("11:22:33:44:55:66", 3)
        json_msg = {'UNKNOWN':{'mac_address':"11:22:33:44:55:66",
                               'port':3}}
        msg2 = SDXMessageUnknownSource(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)

    def test_L2MultipointUnknownSource_init(self):
        msg = SDXMessageL2MultipointUnknownSource("11:22:33:44:55:66", 3)
        json_msg = {'UNKNOWNL2':{'mac_address':"11:22:33:44:55:66",
                               'port':3}}
        msg2 = SDXMessageL2MultipointUnknownSource(json_msg=json_msg)
        self.failUnlessEqual(msg, msg2)


class SDXConnectionEstablishmentTest(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        self.port = 5555

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

    def tearDown(self):
        self.ReceivingSocket.close()

    def receiving_thread(self):
        self.ReceivingSocket.listen(1)
        
        sock, client_address = self.ReceivingSocket.accept()

        self.ServerCxn = SDXControllerConnection(self.ip, self.port,
                                                        sock)
        self.ServerCxn.transition_to_main_phase_SDX(get_initial_rules_5)
        

    def atest_connection_establishment(self):
        print "Beginning connection"
        self.ClientSocket = socket.socket(socket.AF_INET,
                                          socket.SOCK_STREAM)
        self.ClientSocket.connect((self.ip, self.port))
        self.ClientCxn = SDXControllerConnection(self.ip, self.port,
                                                        self.ClientSocket)
        self.ClientCxn.transition_to_main_phase_LC('TESTING', "asdfjkl;",
                                                    install_rule)
        print "pre close"
        self.ClientSocket.close()
        print "close"
                                                    

class SDXConnectionEstablishmentEmptyTest(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        self.port = 5556

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

    def tearDown(self):
        self.ReceivingSocket.close()

    def receiving_thread(self):
        self.ReceivingSocket.listen(1)
        
        sock, client_address = self.ReceivingSocket.accept()

        self.ServerCxn = SDXControllerConnection(self.ip, self.port,
                                                        sock)
        self.ServerCxn.transition_to_main_phase_SDX(get_initial_rules_0)
        

    def test_connection_establishment_empty(self):
        print "Beginning connection"
        self.ClientSocket = socket.socket(socket.AF_INET,
                                          socket.SOCK_STREAM)
        self.ClientSocket.connect((self.ip, self.port))
        self.ClientCxn = SDXControllerConnection(self.ip, self.port,
                                                        self.ClientSocket)
        self.ClientCxn.transition_to_main_phase_LC('TESTING', "asdfjkl;",
                                                    install_rule)
        print "pre close"
        self.ClientSocket.close()
        print "close"

if __name__ == '__main__':
    unittest.main()
