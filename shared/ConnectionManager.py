# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton
from shared.Connection import Connection

import socket
import logging
from threading import Thread
from select import select

class ConnectionManagerTypeError(TypeError):
    pass

class ConnectionManagerValueError(ValueError):
    pass

class ConnectionManager(object):
    ''' This is a parent class for handling connections, dispatching the new 
        connection to handling functions, and otherwise tracking what's going 
        on. One per incoming connection. One for outbound connections. Needs to
        be subclassed, even though much will be in common. Singleton. '''
    __metaclass__ = Singleton

    def __init__(self):
        pass

    def new_connection_callback(self, handling_function):
        ''' Register for a new connection callback. When a new connection comes 
            in, handling_function will be called.
            handling_function should take a Connection as its input. '''
        self.listening_callback = handling_function
    
    def open_listening_port(self, ip, port):
        ''' Opens a listening port. This is a blocking call. Should be run as
            its own thread. '''
        self.listening_address = ip
        self.listening_port = port
        self.listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.listening_sock.bind((self.listening_address,
                                      self.listening_port))
            self.listening_sock.listen(1)
            while True:
                client_sock, client_address = self.listening_sock.accept()
                new_cxn_thread = Thread(target=self._internal_new_connection,
                                        args=(client_sock, client_address))
                new_cxn_thread.daemon = True
                new_cxn_thread.start()

        except:
            raise
    
    def _internal_new_connection(self, sock, address):
        ''' This will call the callback set in new_connection_callback(). Since
            the ConnectionManager handles the connection, it needs to set up 
            tracking of the connection and the like. Creates the Connection, and
            passes this to the saved new connection handling function. 
            Private. '''
        client_ip, client_port = address
        client_connection = Connection(client_ip, client_port, sock)
        self.listening_callback(client_connection)
        
    def open_outbound_connection(self, ip, port):
        ''' This opens an outbound connection to a given address. Returns a 
            Connection that can be used for sending or receiving. '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((ip, port))
        except:
            raise
        return Connection(ip, port, sock)

    def select(self, rlist, wlist, xlist, timeout=0):
        ''' The equivalent of select.select(), but tailored for Connection and
            ConnectionManager. '''
        # Sanity check inputs.
        if (rlist != None):
            for entry in rlist:
                if not isinstance(entry, Connection):
                    raise ConnectionManagerTypeError("rlist must be a list of Connection objects.")
        if (wlist != None):
            for entry in wlist:
                if not isinstance(entry, Connection):
                    raise ConnectionManagerTypeError("wlist must be a list of Connection objects.")
        if (xlist != None):
            for entry in xlist:
                if not isinstance(entry, Connection):
                    raise ConnectionManagerTypeError("xlist must be a list of Connection objects.")
        if not isinstance(timeout, int):
            raise ConnectionManagerTypeError("timeout must be an int")

        rlistsocket = list(map((lambda x: x.sock), rlist))
        wlistsocket = list(map((lambda x: x.sock), wlist))
        xlistsocket = list(map((lambda x: x.sock), xlist))
        
        readable, writable, exceptional = select(rlistsocket,
                                                 wlistsocket,
                                                 xlistsocket,
                                                 timeout)

        # Now, map the sockets back to the Connection
        rcxn = []
        for s_entry in readable:
            for c_entry in rlist:
                if s_entry == c_entry.sock:
                    rcxn.append(c_entry)

        wcxn = []
        for s_entry in writeable:
            for c_entry in wlist:
                if s_entry == c_entry.sock:
                    wcxn.append(c_entry)

        xcxn = []
        for s_entry in exceptional:
            for c_entry in xlist:
                if s_entry == c_entry.sock:
                    xcxn.append(c_entry)

        return (rcxn, wcxn, xcxn)
