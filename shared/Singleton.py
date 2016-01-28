# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project

# Definition of a singleton. This is used heavily by NetAssay.
# Originally defined:
#    https://github.com/sdonovan1985/netassay-ryu/blob/master/base/singleton.py
# Based on:
#    https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
# Example useage:
#    https://github.com/sdonovan1985/netassay-ryu/blob/master/base/mcm.py

class Singleton(type):
    ''' This metaclass is used to define singleton classes. '''

    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


