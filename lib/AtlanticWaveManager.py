from __future__ import absolute_import
# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project


# This provides a base class for "Manager" modules.
# Managers provide a storage and retreival service, typically using a
# database. Each Manager provides the appropriate functions to access the
# particular type of data that the given manager cares about.

from .AtlanticWaveModule import AtlanticWaveModule

class AtlanticWaveManager(AtlanticWaveModule):
    def __init__(self, loggerid, db_filename=":memory:"):

        ''' db_tables_tuples - (attribute_name, db_table_name)
        '''
        super(AtlanticWaveManager, self).__init__(loggerid)
        self.db = None

