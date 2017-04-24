# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX project



# This file is used to define which tables are being used for what porpose. This
# will work for both Corsa- and OVS-based systems.

L2TUNNELTABLE         = 0
SDXEGRESSRULETABLE     = 1
SDXINGRESSRULETABLE    = 2
LEARNINGTABLE          = 2
FORWARDINGTABLE        = 3
LASTTABLE              = 3

ALL_TABLES             = [L2TUNNELTABLE,
                          SDXEGRESSRULETABLE,
                          SDXINGRESSRULETABLE,
                          FORWARDINGTABLE]
ALL_TABLES_EXCEPT_LAST = [L2TUNNELTABLE,
                          SDXEGRESSRULETABLE,
                          SDXINGRESSRULETABLE]
