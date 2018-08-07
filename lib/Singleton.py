# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project

# Definition of a singleton. This is used heavily by NetAssay.
# Originally defined:
#    https://github.com/sdonovan1985/netassay-ryu/blob/master/base/singleton.py
# Based on:
#    https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
#    https://gist.github.com/werediver/4396488
# Example useage:
#    https://github.com/sdonovan1985/netassay-ryu/blob/master/base/mcm.py

import threading

class SingletonMT(type):
    ''' This metaclass is used to define singleton classes. 
    Thread safe?
    This doesn't work for nested Singletons! '''

    _instances_lock = threading.Lock()
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._instances_lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
