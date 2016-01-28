# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton

class CookieManager(object):
    ''' This manages cookies - unique tracking elements for individual rules - 
        for the SDX controller. It hands out unique cookies (well, 32-bits 
        unique), that are restricted to have reserved numbers, such that certain
        numbers are available for the Local Controller to use for its initial 
        setup. Singleton. '''
    __metaclass__ = Singleton
    
    def __init__(self):
        pass

    def get_cookie(self):
        ''' Gets a unique cookie that's not used. '''
        pass

    def release_cookie(self, cookie_number):
        ''' Releases a cookie with cookie_number for reuse. '''
        pass
    
