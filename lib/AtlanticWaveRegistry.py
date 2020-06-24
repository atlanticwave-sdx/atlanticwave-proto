from __future__ import absolute_import
# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project


# This provides a base class for "Registry" modules.
# Registries are for registering functionality, features, or other activities
# that the AtlanticWave/SDX can support. They are often used as a source of
# vaidation (in conjunction with an AtlanticWaveInspector module).

from .AtlanticWaveModule import AtlanticWaveModule

class AtlanticWaveRegistry(AtlanticWaveModule):
    def __init__(self, loggerid):
        super(AtlanticWaveRegistry, self).__init__(loggerid)
