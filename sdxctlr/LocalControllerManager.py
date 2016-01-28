# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from UserManager import UserManager

class LocalControllerManager(UserManager):
    '''Keeps track of authorized Local Controllers. Singleton. '''

    def __init__(self, *args, **kwargs):
        super(LocalControllerManager, self).__init__(*args, **kwargs)
        pass

    def add_controller(self, *args, **kwargs):
        ''' Alias for add_user(). '''
        return self.add_user(*args, **kwargs)

    def remove_controller(self, *args, **kwargs):
        ''' Alias for remove_user(). '''
        return self.remove_user(*args, **kwargs)

    def modify_controller(self, *args, **kwargs):
        ''' Alias for modify_user(). '''
        return self.modify_user(*args, **kwargs)

    def query_controller(self, *args, **kwargs):
        ''' Alias for query_user(). '''
        return self.query_user(*args, **kwargs)
    
