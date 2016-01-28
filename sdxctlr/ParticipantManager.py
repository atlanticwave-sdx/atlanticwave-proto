# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from UserManager import UserManager

class ParticipantManager(UserManager):
    ''' This keeps track of participants and what rights they have. Mostly for
         queries; basically a database. Defining what rights exist, and 
         modifying as such is important here. Singleton. '''

    def __init__(self, *args, **kwargs):
        super(UserManager, self).__init__(*args, **kwargs)
        pass

    def add_participant(self, *args, **kwargs):
        ''' Alias for add_user(). '''
        return self.add_user(*args, **kwargs)

    def remove_participant(self, *args, **kwargs):
        ''' Alias for remove_user(). '''
        return self.remove_user(*args, **kwargs)

    def modify_participant(self, *args, **kwargs):
        ''' Alias for modify_user(). '''
        return self.modify_user(*args, **kwargs)

    def query_participant(self, *args, **kwargs):
        ''' Alias for query_user(). '''
        return self.query_user(*args, **kwargs)
    
