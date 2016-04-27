# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# This starts up the Local Controller for testing.

from localctlr.LocalController import *

lc = LocalController()
lc.start_sdx_controller_connection()
lc.start_main_loop()
