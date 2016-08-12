# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton

class SDXController(object):
    ''' This is the main coordinating module of the SDX controller. It mostly 
        provides startup and coordination, rathe rthan performan many actions by
        itself.
        Singleton. ''' 
    __metaclass__ = Singleton

    def __init__(self):
        pass

    def _setup_logger(self):
        ''' Internal function for setting up the logger formats. '''
        # reused from https://github.com/sdonovan1985/netassay-ryu/blob/master/base/mcm.py
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        console.setFormatter(formatter)
        logfile = logging.FileHandler('sdxcontroller.log')
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(formatter)
        self.logger = logging.getLogger('sdxcontroller')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console)
        self.logger.addHandler(logfile)
