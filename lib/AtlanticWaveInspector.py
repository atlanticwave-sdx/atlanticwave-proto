from __future__ import absolute_import
# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project


# This provides a base class for "Inspector" modules.
# Inspectors are for validating or authenitcating or performsing some sort of
# analysis on given input. They typically work with one or more
# AtlanticWaveManager modules that provides database services for validating
# against.

from .AtlanticWaveModule import AtlanticWaveModule

class AtlanticWaveInspector(AtlanticWaveModule):
    def __init__(self, loggerid):
        super(AtlanticWaveInspector, self).__init__(loggerid)
