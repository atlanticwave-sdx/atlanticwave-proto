# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import json, logging
from shared.Singleton import Singleton
from AuthenticationInspector import AuthenticationInspector
from AuthorizationInspector import AuthorizationInspector

#FIXME: This shouldn't be hard coded.
MANIFEST_FILE = '../manifests/participants.manifest' 

class ParticipantManager(object):
    ''' The ParticipantManager is responsible for keeping track of participant 
        information. This includes keeping track of authentication information 
        for each participant, authorization of different participants (both 
        network operators and scientists), as well as current connectivity.
        Singleton. '''
    __metaclass__ = Singleton

    class ParticipantRecord(object):
        ''' This is used for the current database. '''
        #FIXME: There's a lot more information in the Manifest than here right
        #now.

        def __init__(self, username, credentials, authorizations):
            self.username = username
            self.credentials = credentials
            self.authorizations = authorizations
                     

    def __init__(self):
        ''' The bulk of work is handled at initialization and pushing user 
            information to both the AuthenticationInspector and 
            AuthorizationInspector. '''

        # Setup logging
        self._setup_logger()

        # Setup database. Currently just a dictionary. Probably to be an actual
        # database in the future.
        self.participant_db = {}

        # Setup connections to Authentication and Authorization Inspectors.
        self.AuthenticationInspector = AuthenticationInspector()
        self.AuthorizationInspector = AuthorizationInspector()

        # Parse the manifest into local database
        results = self._parse_manifest(MANIFEST_FILE)
        if results is not None:
            self.participant_db = results
            
        # Push information to the A&A Inspectors.
        for participant in self.participant_db:
            self._send_to_AA(part)


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
        self.logger = logging.getLogger('sdxcontroller.participantmgr')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console)
        self.logger.addHandler(logfile) 
    
    def add_user(self, username, credentials, authorizations):
        ''' This adds users to the ParticipanManager’s database, which will push 
            information to the AuthenticationInspector and 
            AuthorizationInspector. '''
        # Build a partcipant
        participant = ParticipantRecord(username, credentials, authorizations)
        
        # Add to local database
        self.participant_db[particpant.username] = participant
        
        # Push rules to A&A Inspectors
        self._send_to_AA(participant)


    def _parse_manifest(self, manifest_filename):
        with open(manifest_filename) as data_file:
            data = json.load(data_file)

        participants_dict = {}
        for entry in data['participants']:
            participant = ParticipantRecord(entry[username],
                                            entry[credentials],
                                            entry[permitted_actions])
            participants_dict[participant.username] = participant

    def _send_to_AA(self, participant):
        self.AuthenticationInspector.add_user(participant.username,
                                              participant.credentials)
        self.AuthorizationInspector.set_user_authorization(participant.username,
                                                           participant.authorizations)
