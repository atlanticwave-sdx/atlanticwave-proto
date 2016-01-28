# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton

class ConnectionManager(object):
    ''' This is a parent class for handling connections, dispatching the new 
        connection to handling functions, and otherwise tracking what’s going 
        on. One per incoming connection. One for outbound connections. Needs to
        be subclassed, even though much will be in common. Singleton. '''
    __metaclass__ = Singleton

    def __init__(self):
        pass

    def new_connection_callback(self, handling_function):
        ''' Register for a new connection callback. When a new connection comes 
            in, handling_function will be called.
            handling_function should take a Connection as its input. '''
        pass
    
    def open_listening_port(self, ip, port):
        ''' Opens a listening port. '''
        pass
    
    def _internal_new_connection(self):
        ''' This will call the callback set in new_connection_callback(). Since
            the ConnectionManager handles the connection, it needs to set up 
            tracking of the connection and the like. Creates the Connection, and
            passes this to the saved new connection handling function. 
            Private. '''
        pass
    def open_outbound_connection(self):
        ''' This opens an outbound connection to a given address. Returns a 
            Connection that can be used for sending or receiving. '''
        pass
