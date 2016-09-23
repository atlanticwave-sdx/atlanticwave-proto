# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import json, logging
from shared.Singleton import SingletonMixin
from AuthenticationInspector import AuthenticationInspector
from AuthorizationInspector import AuthorizationInspector

#FIXME: This shouldn't be hard coded.
MANIFEST_FILE = '../manifests/participants.manifest' 

class ParticipantManager(SingletonMixin):
    ''' The ParticipantManager is responsible for keeping track of participant 
        information. This includes keeping track of authentication information 
        for each participant, authorization of different participants (both 
        network operators and scientists), as well as current connectivity.
        Singleton. '''

    class ParticipantRecord(object):
        ''' This is used for the current database. '''
        #FIXME: There's a lot more information in the Manifest than here right
        #now.

        def __init__(self, username, credentials, authorizations):
            self.username = username
            self.credentials = credentials
            self.authorizations = authorizations
                     

    def __init__(self, manifest=MANIFEST_FILE):
        ''' The bulk of work is handled at initialization and pushing user 
            information to both the AuthenticationInspector and 
            AuthorizationInspector. '''

        # Setup logging
        self._setup_logger()

        # Setup database. Currently just a dictionary. Probably to be an actual
        # database in the future.
        self.participant_db = {}

        # Parse the manifest into local database
        results = self._parse_manifest(manifest)
        if results is not None:
            self.participant_db = results
            
        # Push information to the A&A Inspectors.
        for username in self.participant_db.keys():
            participant = self.participant_db[username]
            self._send_to_AA(participant)


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
        ''' This adds users to the ParticipanManager's database, which will push 
            information to the AuthenticationInspector and 
            AuthorizationInspector. '''
        # Build a partcipant
        participant = ParticipantManager.ParticipantRecord(username,
                                                           credentials,
                                                           authorizations)
        
        # Add to local database
        self.participant_db[username] = participant
        
        # Push rules to A&A Inspectors
        self._send_to_AA(participant)

    def _get_user(self, username):
        if username not in self.participant_db.keys():
            return None
        return self.participant_db[username]

    def _parse_manifest(self, manifest_filename):
        with open(manifest_filename) as data_file:
            data = json.load(data_file)

        participants_dict = {}

        for username in data['participants'].keys():
            entry = data['participants'][username]
            participant = ParticipantManager.ParticipantRecord(username,
                                             entry['credentials'],
                                             entry['permitted_actions'])
            participants_dict[username] =participant

        return participants_dict

    def _send_to_AA(self, participant):
        AuthenticationInspector.instance().add_user(participant.username,
                                                    participant.credentials)
        AuthorizationInspector.instance().set_user_authorization(participant.username,
                                                                 participant.authorizations)
    
