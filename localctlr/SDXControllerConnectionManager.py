# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.ConnectionManager import ConnectionManager

class SDXControllerConnectionManager(ConnectionManager):
    ''' Used to manage the connection with the SDX Controller. '''

    def __init__(self, *args, **kwargs):
        super(SDXControllerConnectionManager, self).__init__(*args, **kwargs)
