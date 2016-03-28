# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project

# Commands
SDX_NEW_RULE = "NEW_RULE"
SDX_RM_RULE = "RM_RULE"



# Responses




# Connection details
IPADDR = '127.0.0.1'
PORT = 5555

from shared.ConnectionManager import ConnectionManager

class SDXControllerConnectionManager(ConnectionManager):
    ''' Used to manage the connection with the SDX Controller. '''

    def __init__(self, *args, **kwargs):
        super(SDXControllerConnectionManager, self).__init__(*args, **kwargs)
