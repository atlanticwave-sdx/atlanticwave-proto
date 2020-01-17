# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project

# This defines messages between different parts of the LC. Primarily, they're
# used for passing information between the core of the LC and the Switch
# Interface.


# Receives a dictionary {'switch':name, 'port':number, 'src':address}
SM_UNKNOWN_SOURCE = "UNKNOWN_SOURCE"

# Receives a dictionary {'cookie':cookie, 'data':opaque data for handler}
SM_L2MULTIPOINT_UNKNOWN_SOURCE = "L2MULTIPOINT_UNKNOWN_SOURCE"

# Receives nothing - it's a status message.
SM_INTER_RYU_FAILURE = "INTER_RYU_FAILURE"

