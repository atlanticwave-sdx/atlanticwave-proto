# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.ConnectionManager import ConnectionManager

class InterRyuControllerConnectionManager(ConnectionManager):
    ''' Used to manage the connection between parts of the Local Controller. '''

    def __init__(self, *args, **kwargs):
        super(SDXControllerConnectionManager, self).__init__(*args, **kwargs)
