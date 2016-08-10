# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton

class ParticipantManager(object):
    ''' The ParticipantManager is responsible for keeping track of participant 
        information. This includes keeping track of authentication information 
        for each participant, authorization of different participants (both 
        network operators and scientists), as well as current connectivity.
        Singleton. '''
    __metaclass__ = Singleton

    def __init__(self):
        ''' The bulk of work is handled at initialization and pushing user 
            information to both the AuthenticationInspector and 
            AuthorizationInspector. '''
        pass
    
    def add_user(self, username, credentials, authorizations):
        ''' This adds users to the ParticipanManager’s database, which will push 
            information to the AuthenticationInspector and 
            AuthorizationInspector. '''

        pass
