# Copyright 2016 - Sean Donovan
#
# This is the Connection Library for the AtlanticWave/SDX. It is modular and
# much of the functionality can be changed as appropriate.
#
# Initial version is based on pickle and sockets.


import socket
import cPickle as pickle
import logging

DEFAULT_PORT = 15505



class AWConnection(object):


    def __init__(self, address=None, port=None, sock=None):
        # Setup logging
        
        # Allocate resources/init variables
        self.address = address
        self.port = port
        self.sock = sock
        self.sockfile = None
        if self.sock != None:
            self.sockfile = self.sock.makefile()
        



    def open_client_cxn(self, address='127.0.0.1', port=DEFAULT_PORT):
        # This opens up a client TCP connection to a specified server. IPv4 only
        self.address = address
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.sock.connect((self.address, self.port))
            self.sockfile = self.sock.makefile()
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
            connection, client_address = sock.accept()
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
            data = pickle.load(self.sockfile)
            return data
        except:
            raise

    def send(self, data):
        # Sends an item.
        try:
            pickle.dump(data, self.sockfile)
