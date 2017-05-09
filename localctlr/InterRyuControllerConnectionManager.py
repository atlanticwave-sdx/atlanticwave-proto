# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from lib.ConnectionManager import ConnectionManager

# Commands
# RyuControllerInterface to RyuTranslateInterface
ICX_ADD = "ADD"
ICX_REMOVE = "REMOVE"
    

# Responses
# RyuTranslateInterface to RyuControllerInterface
ICX_DATAPATHS = "DATAPATHS"
ICX_UNKNOWN_SOURCE = "UNKNOWN_SOURCE"


class InterRyuControllerConnectionManager(ConnectionManager):
    ''' Used to manage the connection between parts of the Local Controller. '''

    def __init__(self, *args, **kwargs):
        super(InterRyuControllerConnectionManager, self).__init__(*args, **kwargs)

