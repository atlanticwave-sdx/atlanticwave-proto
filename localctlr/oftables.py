# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX project



# This file is used to define which tables are being used for what porpose. This
# will work for both Corsa- and OVS-based systems.

L2TUNNELTABLE          = 0
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



# Which tables to use for specific activities
PRIORITY_DEFAULT                       = 0
#L2TUNNELTABLE - Table 0
PRIORITY_DEFAULT_L2TABLE               = 0
PRIORITY_L2TUNNEL                      = 1
PRIORITY_L2MULTIPOINT                  = 1

#SDXEGRESSRULETABLE - Table 1
PRIORITY_DEFAULT_SDXEGRESS             = 0
PRIORITY_L2MULTIPOINT_TRANSLATE        = 2

#SDXINGRESSRULETABLE - Table 2
PRIORITY_DEFAULT_SDXINGRESS            = 0


#LEARNINGTABLE - Table 2
PRIORITY_GENERIC_LEARNING              = 1
PRIORITY_GENERIC_LEARNED               = 2
PRIORITY_L2MULTIPOINT_LEARNING         = 3
PRIORITY_L2MULTIPOINT_LEARNED          = 4


#FORWARDINGTABLE - Table 3
PRIORITY_DEFAULT_FORWARDING            = 0
PRIORITY_FLOOD_FORWARDING              = 1
PRIORITY_BROADCAST_FORWARDING          = 2
PRIORITY_DESTINATION_FORWARDING        = 2
PRIORITY_L2M_FLOOD_FORWARDING          = 3
PRIORITY_L2M_BROADCAST_FORWARDING      = 4
PRIORITY_L2M_DESTINATION_FORWARDING    = 4
