# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from lib.AtlanticWaveConnectionManager import AtlanticWaveConnectionManager

# Commands
# RyuControllerInterface to RyuTranslateInterface
ICX_ADD = "ADD"
ICX_REMOVE = "REMOVE"
    

# Responses
# RyuTranslateInterface to RyuControllerInterface
ICX_DATAPATHS = "DATAPATHS"
ICX_UNKNOWN_SOURCE = "UNKNOWN_SOURCE"
ICX_L2MULTIPOINT_UNKNOWN_SOURCE = "L2MULTIPOINT_UNKNOWN_SOURCE"


class InterRyuControllerConnectionManager(AtlanticWaveConnectionManager):
    ''' Used to manage the connection between parts of the Local Controller. '''

    def __init__(self, loggeridprefix='localcontroller'):
        loggerid = loggeridprefix + '.interryucontrollercxnmgr'
        super(InterRyuControllerConnectionManager, self).__init__(loggerid)

        self.logger.warning("%s initialized: %s" % (self.__class__.__name__,
                                                    hex(id(self))))
