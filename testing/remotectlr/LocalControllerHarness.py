# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# This starts up the Local Controller for testing.

from localctlr.LocalController import *
from time import sleep

lc = LocalController()

# The LocalController needs to hang around for some period of time after 
# starting. The main loop is run separately in a separate thread.
# Sleeping is a very dirty, but effective, way of keeping it alive.
sleep(30) 
