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
        self.sockfile = None
        if self.sock != None:
            self.sockfile = self.sock.makefile('rwb')

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
            self.sockfile = self.sock.makefile('rwb')
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
            print self.sockfile
            print " before load"
            data = pickle.load(self.sockfile)
            print " after load"
            return data
        except:
            raise

    def send(self, data):
        # Sends an item.
        try:
            print " sending: " + str(data)
            print self.sockfile
            print " before dump"
            pickle.dump(data, self.sockfile)
            print self.sockfile
            print " after dump"
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
                print "Waiting in thread"
                data = pickle.load(self.sockfile)
                print "received something!"
                print "    " + str(data)
                self.recv_cb(data)
        except Error as e:
            # Likely connection going down.
            print e
        
        finally:
            # Clean up connectiong
            self.close()
        
        
    def start_receive_thread(self):
        # Spawn a new thread to listen for receives.
        if self.recv_cb == None:
            raise AWConnectionError("recv_cb not filled in")
        self.recv_thread = threading.Thread(target=self._receive_thread)
        self.recv_thread.daemon = True
        print " starting thread"
        self.recv_thread.start()
        print " after starting thread"

        

        
