# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import socket
import select as pyselect
import cPickle as pickle
import logging
import threading
import sys
import struct

class ConnectionTypeError(TypeError):
    pass

class ConnectionValueError(ValueError):
    pass


class Connection(object):
    ''' Handed out by the ConnectionManager. It's basically the same as a 
        traditional socket, but can be very different under the hood. Initially,
        it'll be a socket, but in the future, this can be changed to be a TLS 
        socket, for instance. '''

    def __init__(self, address, port, sock):
        # Setup logging

        # Validate incoming variables
        # Skipping address and port for now.
        if type(sock) is not socket.socket:
            raise TypeError("sock is not a socket: " + str(type(sock)))
        
        # Allocate resources/init variables
        self.address = address
        self.port = port
        self.sock = sock

        self.recv_cb = None
        self.recv_thread = None
        
    def __del__(self):
        # Destructor
        try:
            self.close()
        except:
            pass

    def get_address(self):
        return self.address
    def get_port(self):
        return self.port
    def get_socket(self):
        return self.sock

    
    def recv(self):
        ''' Receives an item. This is a blocking call. '''
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
            return data

        except:
            raise


    def send(self, data):
        ''' Sends an item. '''
        try:
            # Based on https://code.activestate.com/recipes/408859-socketrecv-three-ways-to-turn-it-into-recvall/
            data_raw = pickle.dumps(data)
            self.sock.sendall(struct.pack('>i', len(data_raw))+data_raw)
        except:
            raise
        pass

    def close(self):
        ''' Close out the connection. '''
        try:
            self.sock.close()
        except:
            raise

    def register_receive_callback(self, callback):
        ''' If using non-blocking receive, this saves the callback that receives
            data. 
            callback takes one item as its input (any type it chooses). '''
        self.recv_cb = callback

    def start_receive_thread(self):
        ''' This starts a separate thread for receiving data. It will call back
            the callback set in register_receive_callback(). '''
        if self.recv_cb == None:
            raise ConnectionError("recv_cb not filled in")
        self.recv_thread = threading.Thread(target=self._receive_thread)
        self.recv_thread.daemon = True
        self.recv_thread.start()

    def _receive_thread(self):
        ''' The actual thread that receives items. Private. '''
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

    

def select(rlist, wlist, xlist, timeout=0):
    ''' The equivalent of select.select(), but tailored for Connection and
        ConnectionManager. '''
    # Sanity check inputs.
    if (rlist != None):
        for entry in rlist:
            if not isinstance(entry, Connection):
                raise ConnectionTypeError("rlist must be a list of Connection objects.")
    if (wlist != None):
        for entry in wlist:
            if not isinstance(entry, Connection):
                raise ConnectionTypeError("wlist must be a list of Connection objects.")
    if (xlist != None):
        for entry in xlist:
            if not isinstance(entry, Connection):
                raise ConnectionTypeError("xlist must be a list of Connection objects.")
    if not isinstance(timeout, int):
        raise ConnectionTypeError("timeout must be an int")

    rlistsocket = list(map((lambda x: x.sock), rlist))
    wlistsocket = list(map((lambda x: x.sock), wlist))
    xlistsocket = list(map((lambda x: x.sock), xlist))
        
    readable, writable, exceptional = pyselect.select(rlistsocket,
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
    for s_entry in writable:
        for c_entry in wlist:
            if s_entry == c_entry.sock:
                wcxn.append(c_entry)

    xcxn = []
    for s_entry in exceptional:
        for c_entry in xlist:
            if s_entry == c_entry.sock:
                xcxn.append(c_entry)

    return (rcxn, wcxn, xcxn)
