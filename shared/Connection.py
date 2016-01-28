# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


class Connection(object):
    ''' Handed out by the ConnectionManager. It’s basically the same as a 
        traditional socket, but can be very different under the hood. Initially,
        it’ll be a socket, but in the future, this can be changed to be a TLS 
        socket, for instance. '''

    def __init__(self):
        pass

    def recv(self):
        pass

    def send(self):
        pass

    def close(self):
        pass

    def register_receive_callback(self, callback):
        ''' If using non-blocking receive, this saves the callback that receives
            data. 
            callback takes one item as its input (any type it chooses). '''
        pass

    def start_receive_thread(self):
        ''' This starts a separate thread for receiving data. It will call back
            the callback set in register_receive_callback(). '''
        pass

    def _receive_thread(self):
        ''' The actual thread that receives items. Private. '''
        pass

    

