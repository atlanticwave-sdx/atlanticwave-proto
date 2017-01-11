# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project

# DEFINEs, from the OpenFlow 1.3.2 spec.
OFPP_MAX         = 0xffffff00
OFPP_IN_PORT     = 0xfffffff8
OFPP_TABLE       = 0xfffffff9
OFPP_NORMAL      = 0xfffffffa
OFPP_FLOOD       = 0xfffffffb
OFPP_ALL         = 0xfffffffc
OFPP_CONTROLLER  = 0xfffffffd
OFPP_LOCAL       = 0xfffffffe
OFPP_ANY         = 0xffffffff


OFPCML_MAX       = 0xffe5
OFPCML_NO_BUFFER = 0xffff

OF_TABLE_MIN      = 0
OF_TABLE_MAX      = 255
OF_PRIORITY_MIN   = 0
OF_PRIORITY_MAX   = 16535
OF_COOKIE_MIN     = 0
OF_COOKIE_MAX     = 16535

# These may be deletable. I think I wrote them.
OFM_NUMBER      = 1
OFM_BITMASK     = 2
OFM_IPV4        = 3
OFM_IPV6        = 4
OFM_PREFIX_V4   = 5
OFM_PREFIX_V6   = 6

