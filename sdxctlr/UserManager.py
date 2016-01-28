# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton

class UserManager(object):
    ''' Parent class for both deciding who are known external entities. 
        Singleton. ''' 
    __metaclass__ = Singleton

    def __init__(self):
        pass

    def add_user(self):
        pass

    def remove_user(self):
        pass

    def modify_user(self):
        pass

    def query_user(self):
        pass
