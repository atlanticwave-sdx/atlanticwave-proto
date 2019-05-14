# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project

# Unit tests for shared.SDXControllerConnectionManager

import unittest
import threading
import socket
from time import sleep
from shared.SDXControllerConnectionManager import *
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

class InitTest(unittest.TestCase):
    def test_singleton(self):
        firstManager = SDXControllerConnectionManager()
        secondManager = SDXControllerConnectionManager()

        self.failUnless(firstManager is secondManager)

class OpenListeningPortTest(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        self.port = 5565
        self.manager = None
        self.clientcxn = None
        self.servercxn = None
        self.clientstate = None
        self.serverstate = None

    def tearDown(self):
        self.manager.close_listening_port()

    def listening_thread(self):
        self.manager.new_connection_callback(self.receiving_thread)
        self.manager.open_listening_port(self.ip, self.port)

    def receiving_thread(self, cxn):
        self.servercxn = cxn
        self.servercxn.transition_to_main_phase_SDX(get_initial_rules_0)
        self.serverstate = self.servercxn.get_state()


    def sending_thread(self):
        client_sock = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)
        client_sock.connect((self.ip, self.port))
        self.clientcxn = SDXControllerConnection(self.ip, self.port,
                                                 client_sock)

        self.clientcxn.transition_to_main_phase_LC('TESTING', 'asdfjkl;',
                                                   install_rule)
        self.clientstate = self.clientcxn.get_state()

                                
    def test_open_listening_port(self):
        self.manager = SDXControllerConnectionManager()

        self.ListeningThread = threading.Thread(target=self.listening_thread)
        self.ListeningThread.daemon = True
        self.ListeningThread.start()

        self.SendThread = threading.Thread(target=self.sending_thread)
        self.SendThread.daemon = True
        self.SendThread.start()
        

        sleep(0.1) # Rather than messing about with locks
        self.failUnlessEqual(self.clientstate, "MAIN_PHASE")
        self.failUnlessEqual(self.serverstate, "MAIN_PHASE")

class OpenSendPortTest(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        self.port = 5566
        self.manager = None
        self.clientcxn = None
        self.servercxn = None

    def tearDown(self):
        if self.clientcxn != None:
            self.clientcxn.close()
        if self.servercxn != None:
            self.servercxn.close()
            

    def listening_thread(self):
        self.receiving_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_STREAM)
        self.receiving_socket.bind((self.ip, self.port))
        self.receiving_socket.listen(1)

        sock, client_address = self.receiving_socket.accept()
        self.servercxn = SDXControllerConnection(self.ip, self.port, sock)
        self.servercxn.transition_to_main_phase_SDX(get_initial_rules_0)
        self.serverstate = self.servercxn.get_state()


    def sending_thread(self):
        self.clientcxn = self.manager.open_outbound_connection(self.ip,
                                                               self.port)

        self.clientcxn.transition_to_main_phase_LC('TESTING', 'qweruiop',
                                                   install_rule)
        self.clientstate = self.clientcxn.get_state()


    def test_open_send_port(self):
        self.manager = SDXControllerConnectionManager()

        self.ListeningThread = threading.Thread(target=self.listening_thread)
        self.ListeningThread.daemon = True
        self.ListeningThread.start()

        self.SendThread = threading.Thread(target=self.sending_thread)
        self.SendThread.daemon = True
        self.SendThread.start()

        sleep(0.1) # Rather than messing about with locks
        self.failUnlessEqual(self.clientstate, "MAIN_PHASE")
        self.failUnlessEqual(self.serverstate, "MAIN_PHASE")
        
        

        
if __name__ == '__main__':
    unittest.main()
