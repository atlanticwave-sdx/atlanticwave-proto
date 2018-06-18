# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project


# This provides a base class for "Manager" modules.
# Managers provide a storage and retreival service, typically using a
# database. Each Manager provides the appropriate functions to access the
# particular type of data that the given manager cares about.

from AtlanticWaveModule import AtlanticWaveModule

class AtlanticWaveManager(AtlanticWaveModule):
    def __init__(self, loggerid, logfilename, db_tables_tuples,
                 db_filename=":memory:",debuglogfilename=None):

        ''' db_tables_tuples - (attribute_name, db_table_name)
        '''
        super(AtlanticWaveManager, self).__init__(loggerid, logfilename,
                                                  debuglogfilename)
        self.db = None

