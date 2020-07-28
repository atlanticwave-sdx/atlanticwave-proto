from __future__ import print_function
from __future__ import unicode_literals
# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project

# Unit tests for lib.Connection module.

from future import standard_library
standard_library.install_aliases()
import unittest
import socket
import threading
import pickle as pickle
from time import sleep
from lib.Connection import *
import pynetstring

class InitTest(unittest.TestCase):
    def test_empty_init(self):
        try:
            Connection()
        except TypeError:
            pass
        else:
            self.fail('Did not see Error')

    def test_invalid_socket(self):
        ip = "127.0.0.1"
        port = 5555
        sock = "dummy sock"
        try:
            cxn = Connection(ip, port, sock)
        except TypeError:
            pass
        else:
            self.fail('Did not see Error')
            
    def test_basic_init(self):
        ip = "127.0.0.1"
        port = 5555
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cxn = Connection(ip, port, sock)
        self.assertEqual(cxn.get_address(), "127.0.0.1")
        self.assertEqual(cxn.get_port(), 5555)
        self.assertEqual(cxn.get_socket(), sock)
        print(cxn.__repr__())
        print(cxn)
                             


class SendTest(unittest.TestCase):
    def setUp(self):

        self.ip = "127.0.0.1"
        self.port = 5551
        self.object_to_send = {'a':1, 'b':2, 'c':{'x':7, 'y':8, 'z':9}}
        self.object_received = None
        
        self.ReceivingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ReceivingSocket.bind((self.ip, self.port))
        self.ReceiveThread = threading.Thread(target=self.receiving_thread)
        self.ReceiveThread.daemon = True
        self.ReceiveThread.start()
        sleep(.5)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.ip, self.port))
        self.SendingSocket = Connection(self.ip, self.port, sock)

    def tearDown(self):
        self.ReceivingSocket.close()

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
                size = sys.maxsize
                size_data = b''
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
                            data_raw = b"".join(total_data)
                        else:
                            size_data += sock_data
                        
                    else:
                        total_data.append(sock_data)
                        total_len = sum([len(i) for i in total_data])
                        data_raw = b"".join(total_data)

                # Unpickle!
                data = pickle.loads(data_raw)
                self.object_received = data
            
        finally:
            # Clean up the connection
            connection.close()

                
    def test_send(self):
        self.SendingSocket.send(self.object_to_send)
        sleep(0.25 )  # Rather than messing about with locks.
        print(self.object_received)
        print(self.object_to_send)
        self.assertEqual(self.object_received, self.object_to_send)


class RecvBlockingTest(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        self.port = 5557
        self.object_to_send = {'a':1, 'b':2, 'c':{'x':7, 'y':8, 'z':9}}

        self.ReceivingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ReceivingSocket.bind((self.ip, self.port))
        self.ReceivingSocket.listen(1)

        self.SendThread = threading.Thread(target=self.sending_thread)
        self.SendThread.daemon = True
        self.SendThread.start()

        connection, client_address = self.ReceivingSocket.accept()
        client_ip, client_port = client_address
        
        self.ReceivingConnection = Connection(client_ip, client_port, connection)        

    def tearDown(self):
        self.ReceivingSocket.close()

    def sending_thread(self):
        self.SendingSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SendingSock.connect((self.ip, self.port))
        
        data_raw = pickle.dumps(self.object_to_send)
        self.SendingSock.sendall(struct.pack('>i', len(data_raw))+data_raw)
        self.SendingSock.close()

    def test_blocking_receive(self):
        data = self.ReceivingConnection.recv()
        self.ReceivingConnection.close()
        print(data)
        print(self.object_to_send)
        self.assertEqual(data, self.object_to_send)


class RecvNonBlockingTest(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        self.port = 5558
        self.object_to_send = {'a':1, 'b':2, 'c':{'x':7, 'y':8, 'z':9}}
        self.object_received = None

        self.ReceivingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ReceivingSocket.bind((self.ip, self.port))
        self.ReceivingSocket.listen(1)

        self.SendThread = threading.Thread(target=self.sending_thread)
        self.SendThread.daemon = True
        self.SendThread.start()

        connection, client_address = self.ReceivingSocket.accept()
        client_ip, client_port = client_address
        
        self.ReceivingConnection = Connection(client_ip, client_port, connection)           

    def tearDown(self):
        self.ReceivingSocket.close()

    def sending_thread(self):
        self.SendingSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SendingSock.connect((self.ip, self.port))
        
        data_raw = pickle.dumps(self.object_to_send)
        self.SendingSock.sendall(struct.pack('>i', len(data_raw))+data_raw)
        self.SendingSock.close()

    def test_blocking_receive(self):
        self.ReceivingConnection.register_receive_callback(self.receiving_callback)
        self.ReceivingConnection.start_receive_thread()
        sleep(0.25) # Rather than messing about with locks.
        self.assertEqual(self.object_received, self.object_to_send)

    def receiving_callback(self, data):
        self.object_received = data


class ValidSelectTest(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        self.port = 5559
        self.object_to_send = {'a':1, 'b':2, 'c':{'x':7, 'y':8, 'z':9}}
        self.object_received = None

        self.ReceivingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ReceivingSocket.bind((self.ip, self.port))
        self.ReceivingSocket.listen(1)

        self.SendThread = threading.Thread(target=self.sending_thread)
        self.SendThread.daemon = True
        self.SendThread.start()

        connection, client_address = self.ReceivingSocket.accept()
        client_ip, client_port = client_address
        
        self.ReceivingConnection = Connection(client_ip, client_port, connection)
        
    def tearDown(self):
        self.ReceivingSocket.close()

    def sending_thread(self):
        self.SendingSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SendingSock.connect((self.ip, self.port))

        sleep(0.25)
        
        data_raw = pickle.dumps(self.object_to_send)
        self.SendingSock.sendall(struct.pack('>i', len(data_raw))+data_raw)
        self.SendingSock.close()

    def test_basic_select(self):
        cxn = self.ReceivingConnection
        rlist = [cxn]
        wlist = []
        xlist = rlist

        readable, writable, exceptional = select(rlist, wlist, xlist, 2.0)

        self.assertFalse(readable == [])

        self.object_received=cxn.recv()
        self.assertEqual(self.object_received, self.object_to_send)

class invalidSelectTest(unittest.TestCase):
    def test_invalid_select_init1(self):
        ip = "127.0.0.1"
        port = 5560
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cxn = Connection(ip, port, sock)
        goodlist = [cxn]
        badlist = [ip]
        emptylist = []

        try:
            r, w, x = select(badlist, goodlist, goodlist)
        except TypeError:
            pass
        else:
            self.fail('Did not see error')

        try:
            r, w, x = select(goodlist, badlist, goodlist)
        except TypeError:
            pass
        else:
            self.fail('Did not see error')

        try:
            r, w, x = select(goodlist, goodlist, badlist)
        except TypeError:
            pass
        else:
            self.fail('Did not see error')

if __name__ == '__main__':
    unittest.main()
