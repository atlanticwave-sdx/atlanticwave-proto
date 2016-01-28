# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.ConnectionManager import ConnectionManager

class UserConnectionManager(ConnectionManager):
    ''' Used to manage the connections with the Participants. '''

    def __init__(self, *args, **kwargs):
        super(UserConnectionManager, self).__init__(*args, **kwargs)
