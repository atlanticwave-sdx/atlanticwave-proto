# Copyright 2016 - Sean Donovan
#
# This is the Connection Library for the AtlanticWave/SDX. It is modular and
# much of the functionality can be changed as appropriate.
#
# Initial version is based on pickle and sockets.


import socket
import cPickle as pickle
import logging
import threading
import sys
import struct

DEFAULT_PORT = 15505

class AWConnectionError(Exception):
    pass


class AWConnection(object):


    def __init__(self, address=None, port=None, sock=None):
        # Setup logging
        
        # Allocate resources/init variables
        self.address = address
        self.port = port
        self.sock = sock

        self.recv_cb = None
        self.recv_thread = None
        
    def __del__(self):
        # Destructor
        self.close()



    def open_client_cxn(self, address='127.0.0.1', port=DEFAULT_PORT):
        # This opens up a client TCP connection to a specified server. IPv4 only
        self.address = address
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.sock.connect((self.address, self.port))
        except:
            raise


    def open_server_cxn(self, address='127.0.0.1', port=DEFAULT_PORT):
        # This opens up a server listening socket.
        self.address = address
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.sock.bind((self.address, self.port))
            self.sock.listen(1)
        except:
            raise

    def server_cxn_accept(self):
        # Returns a new connection AWConnection and a client address
        try:
            connection, client_address = self.sock.accept()
            clientcxn = AWConnection(self.address, self.port, connection)
            return (clientcxn, client_address)
        except:
            raise

    def close(self):
        # Close out the connection.
        try:
            self.sock.close()
        except:
            raise

    def recv(self):
        # Receives an item. This is a blocking call
        try:
            # Based on https://code.activestate.com/recipes/408859-socketrecv-three-ways-to-turn-it-into-recvall/
            total_len = 0
            total_data = []
            size = sys.maxint
            size_data = ''
            sock_data = ''
            recv_size = 8192
            while total_len < size:
                sock_data = self.sock.recv(recv_size)
                if not total_data:
                    if len(sock_data) > 4:
                        size_data += sock_data
                        size = struct.unpack('>i', size_data[:4])[0]
                        recv_size=size
                        if recv_size>524288 :
                            recv_size = 524288
                        total_data.append(size_data[4:])
                    else:
                        size_data += sock_data
                else:
                    total_data.append(sock_data)
                total_len = sum([len(i) for i in total_data])
            data_raw = ''.join(total_data)

            # Unpickle!
            data = pickle.loads(data_raw)
            return data

        except:
            raise

    def send(self, data):
        # Sends an item.
        try:
            # Based on https://code.activestate.com/recipes/408859-socketrecv-three-ways-to-turn-it-into-recvall/
            data_raw = pickle.dumps(data)
            self.sock.sendall(struct.pack('>i', len(data_raw))+data_raw)
        except:
            raise

    def register_receive_callback(self, callback):
        # Registers a callback. Need to call start_receive_thread() in order to
        # receiver anything thorugh the callback.
        self.recv_cb = callback

    def _receive_thread(self):
        # Inner workings of receive work.
        try:
            while True:
                data = self.recv()
                self.recv_cb(data)
        except Error as e:
            # Likely connection going down.
            pass
        
        finally:
            # Clean up connectiong
            self.close()
        
        
    def start_receive_thread(self):
        # Spawn a new thread to listen for receives.
        if self.recv_cb == None:
            raise AWConnectionError("recv_cb not filled in")
        self.recv_thread = threading.Thread(target=self._receive_thread)
        self.recv_thread.daemon = True
        self.recv_thread.start()

        

        
