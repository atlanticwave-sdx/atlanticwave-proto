# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project

# Unit tests for shared.ConnectionManager module.

import unittest
import threading
from time import sleep
from shared.ConnectionManager import *
from shared.Connection import *

class InitTest(unittest.TestCase):
    def test_singleton(self):
        firstManager = ConnectionManager()
        secondManager = ConnectionManager()

        self.failUnless(firstManager is secondManager)



class OpenListeningPortTest(unittest.TestCase):
    def setUp(self):
        self.manager = ConnectionManager()
        self.ip = "127.0.0.1"
        self.port = 5560
        self.object_to_send = {'a':1, 'b':2, 'c':{'x':7, 'y':8, 'z':9}}
        self.object_received = None
        
    def test_open_listening_port(self):
        self.ListeningThread = threading.Thread(target=self.listening_thread)
        self.ListeningThread.daemon = True
        self.ListeningThread.start()
        
        self.SendThread = threading.Thread(target=self.sending_thread)
        self.SendThread.daemon = True
        self.SendThread.start()
        
        sleep(0.1) # Rather than messing about with locks.
        self.failUnlessEqual(self.object_received, self.object_to_send)

    def listening_thread(self):
        self.manager.new_connection_callback(self.receiving_thread)
        self.manager.open_listening_port(self.ip, self.port)

    def sending_thread(self):
        self.SendingSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SendingSock.connect((self.ip, self.port))
        
        data_raw = pickle.dumps(self.object_to_send)
        self.SendingSock.sendall(struct.pack('>i', len(data_raw))+data_raw)
        self.SendingSock.close()

    def receiving_thread(self, cxn):
        self.ReceivingConnection = cxn
        data = self.ReceivingConnection.recv()
        self.object_received = data
        self.ReceivingConnection.close()


class OpenSendingText(unittest.TestCase):
    def setUp(self):
        self.manager = ConnectionManager()
        self.ip = "127.0.0.1"
        self.port = 5561
        self.object_to_send = {'a':1, 'b':2, 'c':{'x':7, 'y':8, 'z':9}}
        self.object_received = None

        self.ReceivingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ReceivingSocket.bind((self.ip, self.port))
        self.ReceiveThread = threading.Thread(target=self.receiving_thread)
        self.ReceiveThread.daemon = True
        self.ReceiveThread.start()

        print self.manager.__repr__()
        print self.manager

    def test_sending_port(self):
        cxn = self.manager.open_outbound_connection(self.ip, self.port)

        cxn.send(self.object_to_send)
        sleep(0.1 )  # Rather than messing about with locks.
        self.failUnlessEqual(self.object_received, self.object_to_send)        

    def receiving_thread(self):
        # Based on https://pymotw.com/2/socket/tcp.html,
        # https://code.activestate.com/recipes/408859-socketrecv-three-ways-to-turn-it-into-recvall/
        self.ReceivingSocket.listen(1)

        connection, client_address = self.ReceivingSocket.accept()

        try:

            # Receive the data in small chunks and retransmit it
            while True:
                total_len = 0
                total_data = []
                size = sys.maxint
                size_data = ''
                sock_data = ''
                recv_size = 8192
                while total_len < size:
                    sock_data = connection.recv(recv_size)
                    if not total_data:
                        if len(sock_data) > 4:
                            size_data += sock_data
                            size = struct.unpack('>i', size_data[:4])[0]
                            recv_size=size
                            if recv_size>524288 :
                                recv_size = 524288
                            total_data.append(size_data[4:])
                            total_len = sum([len(i) for i in total_data])
                            data_raw = ''.join(total_data)
                        else:
                            size_data += sock_data
                        
                    else:
                        total_data.append(sock_data)
                        total_len = sum([len(i) for i in total_data])
                        data_raw = ''.join(total_data)

                # Unpickle!
                data = pickle.loads(data_raw)
                self.object_received = data
            
        finally:    
            # Clean up the connection
            connection.close()


        

        
if __name__ == '__main__':
    unittest.main()
