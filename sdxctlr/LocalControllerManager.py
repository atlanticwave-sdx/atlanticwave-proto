# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import json, logging
from shared.Singleton import Singleton
from AuthenticationInspector import AuthenticationInspector
from TopologyManager import TopologyManager

#FIXME: This shouldn't be hard coded.
MANIFEST_FILE = '../manifests/localcontroller.manifest'

class LocalControllerManagerValueError(ValueError):
    pass

class LocalControllerManager(object):
    ''' The LocalControllerManager is responsible for keeping track of local 
        controller information, in particular authorization information for 
        different local controllers. In the future, this may also include 
        information as to capabilities present at different local controllers 
        (i.e., different switch capabilities).
        Singleton. '''
    __metaclass__ = Singleton

    class LCRecord(object):
        ''' This is used for the current database. '''
        #FIXME: There's a lot more information in the Manifest than here right now.
        def __init__(self, shortname, credentials, lcip, switchips,
                     connected=False):
            self.shortname = shortname
            self.credentials = credentials
            self.lcip = lcip
            self.switchips = switchips
            self.connected = connected

        def set_connected(self):
            self.connected = True

        def set_disconnected(self):
            self.connected = True
        
    
    def __init__(self, manifest=MANIFEST_FILE):
        ''' The bulk of work is handled at initialization and pushing user 
            information to both the AuthenticationInspector and 
            AuthorizationInspector. '''

        # Setup logging
        self._setup_logger()

        # Setup database. Currently just a dictionary. Probably to be an actual
        # database in the future.
        self.localctlr_db = {}

        # Setup connections to AuthenticationInspector and the CxnMgr.
        self.AuthenticationInspector = AuthenticationInspector()

        # Parse the manifest into local database
        results = self._parse_manifest(manifest)
        if results is not None:
            self.localctlr_db = results
            
        # Push information to the A&A Inspectors.
        for ctlr in self.localctlr_db:
            self._send_to_AI(cltr)


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
        self.logger = logging.getLogger('sdxcontroller.localctlrmgr')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console)
        self.logger.addHandler(logfile) 

    def add_controller(self, controller, credentials, lcip, switchips):
        ''' This adds users to the LocalControllerManager’s database, which will 
            push information to the AuthenticationInspector. '''
        rec = LCRecord(shortname, credentials, lcip, switchips)
        self.localctlr_db[shortname] = rec
        self._send_to_AI(rec)

    def new_controller_connection(self, controllerip):
        '''This is called by the SDXController when a new local controller 
           connects which informs the TopologyManager of the change. '''
        for key in self.localctlr_db.keys():
            entry = self.localctlr_db[key]:
            if entry.lcip == controllerip:
                entry.set_connected()
                return

        raise LocalControllerValueError("new_controller_connection: %s is not registered as a controller IP address." % controllerip)
        
        
    def remove_controller_connection(self, controllerip):
        ''' When a local controller has disconnected, this is called. '''
        for key in self.localctlr_db.keys():
            entry = self.localctlr_db[key]:
            if entry.lcip == controllerip:
                entry.set_disconnected()
                return

        raise LocalControllerValueError("remove_controller_connection: %s is not registered as a controller IP address." % controllerip)

    
    def _parse_manifest(self, manifest_filename):
        with open(manifest_filename) as data_file:
            data = json.load(data_file)

        for key in data['localcontrollers']:
            entry = data['localcontrollers'][key]
            shortname = entry['shortname']
            credentials = entry['credentials']
            lcip = entry['lcip']
            switchips = []
            for sw in entry['switchinfo']:
                switchips.append(sw['ip'])

            # Build the LCRecord and add it to the DB
            rec = LCRecord(shortname, credentials, lcip, switchips)
            self.localctlr_db[shortname] = rec
        
    def _send_to_AI(self, ctlr):
        self.AuthenticationInspector.add_user(cltr.shortname,
                                              ctlr.credentials)
