# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
from shared.Singleton import Singleton

class AuthenticationInspector(object):
    ''' The AuthenticationInspector is responsible for determining if someone or
        something is authenticated (is who they say they are). It receives 
        information from both the ParticipantManager and the 
        LocalControllerManager about the credentials of the participants and 
        local controllers, respectively.
        Singleton. ''' 
    __metaclass__ = Singleton

    def __init__(self):
        # Setup logger
        self._setup_logger()

        # Initialize the credential store
        self._credential_store = {}

        self.logger.debug("AuthenticationInspector initialized.")

        

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
        self.logger = logging.getLogger('sdxcontroller.authentication')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console)
        self.logger.addHandler(logfile) 


    def is_authenticated(self, username, credentials):
        ''' Returns true if user is authenticated, False otherwise. Credentials 
            may change over time, for instance, for the initial deployment, 
            credentials could be a hashed password, while later it will be a 
            certificate/cert operation. ''' 
        if username not in self._credential_store.keys():
            self.logger.warning('User does not exist: %s', username)
            return False
        if self._credential_store[username] != credentials:
            self.logger.warning('User provided incorrect credentials: %s, %s',
                                username, credentials)
            return False

        self.logger.debug('User logged in successfully: %s', username)
        return True

    
    def add_user(self, username, credentials):
        ''' This is used by both the ParticipantManager and 
            LocalControllerManager to add a single user, credential pair that 
            is authorized. '''
        if username in self._credential_store.keys():
            self.logger.info('User\'s credentials changing: %s', username)
        else:
            self.logger.info('New user being added to store: %s', username)

        self._credential_store[username] = credentials

        
    def add_users(self, list_of_authentications):
        ''' Used to add a list of user, credential pairs. List_of_authentications
            is a list of user, credential tuples.
            Initial implementation will just loop through the elements in the 
            list and call add_user. '''

        self.logger.debug('Adding %d users', len(list_of_authentications))

        for (username, credentials) in list_of_authentications:
            self.add_user(username, credentials)
