# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.ConnectionManager import ConnectionManager

class LocalControllerConnectionManager(ConnectionManager):
    ''' Used to manage the connections with the Local Controllers. '''

    def __init__(self, *args, **kwargs):
        super(LocalControllerConnectionManager, self).__init__(*args, **kwargs)
