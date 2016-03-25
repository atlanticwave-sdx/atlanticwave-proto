# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.ConnectionManager import ConnectionManager

# Commands
ICX_ADD = "ADD"
ICX_REMOVE = "REMOVE"
    

# Responses
ICX_DATAPATHS = "DATAPATHS"


class InterRyuControllerConnectionManager(ConnectionManager):
    ''' Used to manage the connection between parts of the Local Controller. '''

    def __init__(self, *args, **kwargs):
        super(InterRyuControllerConnectionManager, self).__init__(*args, **kwargs)

