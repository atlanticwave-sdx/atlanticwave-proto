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

class Singleton(type):
    ''' This metaclass is used to define singleton classes. 
    This doesn't work for nested Singletons! '''

    _instances_lock = threading.Lock()
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._instances_lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonMixin(object):
	__singleton_lock = threading.Lock()
	__singleton_instance = None

	@classmethod
	def instance(cls, *args, **kwargs):
            if not cls.__singleton_instance:
                with cls.__singleton_lock:
                    if not cls.__singleton_instance:
                        cls.__singleton_instance = cls(*args, **kwargs)
            return cls.__singleton_instance

