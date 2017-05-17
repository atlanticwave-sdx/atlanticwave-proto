# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project

# This defines messages from the LC to the SDX Controller. These messages are
# generated at the LC, but at any layer in the LC.


# Receives a dictionary {'switch':name, 'port':number, 'src':address}
SM_UNKNOWN_SOURCE = "UNKNOWN_SOURCE"

# Receives a dictionary {'cookie':cookie, 'data':opaque data for handler}
SM_L2MULTIPOINT_UKNOWN_SOURCE = "L2MULTIPOINT_UKNOWN_SOURCE"
