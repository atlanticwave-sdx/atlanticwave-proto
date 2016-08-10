# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


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
        pass

    def _setup_logger(self):
        ''' Internal function for setting up the logger formats. '''
        pass


    def is_authenticated(self, username, credentials):
        ''' Returns true if user is authenticated, False otherwise. Credentials 
            may change over time, for instance, for the initial deployment, 
            credentials could be a hashed password, while later it will be a 
            certificate/cert operation. ''' 
        pass

    def add_user(self, username, credentials):
        ''' This is used by both the ParticipantManager and 
            LocalControllerManager to add a single user, credential pair that 
            is authorized. '''
        pass

    def add_users(self, list_of_authentications):
        ''' Used to add a list of user, credential pairs. List_of_authentications
            is a list of user, credential tuples.
            Initial implementation will just loop through the elements in the 
            list and call add_user. '''

        for (username, credentials) in list_of_authentications:
            self.add_user(username, credentials)
