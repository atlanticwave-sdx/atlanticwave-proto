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

# NOTE: Remember how OpenFlow flowmods work. They have three parts (that we care
# about:
#    - match(es)
#    - action(s)
#    - metadata
# This file only concerns the first two, and doesn't concern the metadata,
# including cookies and priorities.



# For validation, we will use a special dictionaries, specified below, to allow
# for an extensible definition of what is allowed by OpenFlow. This allows us
# to define only the OpenFlow matches and actions that we will support at any
# given time. Initially, this will be very basic: only supporting the bare
# minimum. In later development, this will be extended to match the full
# OpenFlow 1.3 specification.

# For matches, a dictionary with the following fields will be used:
#    header    - Text definition of the match header field.
#    type      - This is the type of value to expect for this header. It has
#                the following list of valid types. Some will use a validator
#                (function that checks if something is an IP address, for
#                instance), while others will have additional fields, both named
#                after the hyphen.
#        number       - min, max, other
#                       'other' is used rarely - only for cases when something
#                       could be 0-65530 or 65535 and there are reserved numbers
#        bitmask      - min, max
#        IPaddress4   - IPv4 Validator
#        IPaddress6   - IPv6 Validator
#        Prefix4      - IPv4 Prefix Validator
#        Prefix6      - IPv6 Prefix Validator
#    mask      - True if masks are allowed, False otherwise
#    prereqs   - List of Prerequisites. Possible list of items that at least one
#                must be true before this header is valid. IP Protocol 6 for TCP
#                srcport, for instance. These headers will be verified, in turn.
#                These will be in a separate dictionary using the following:
#        header   - The name of the header (must be defined in this table).
#        value    - The value it will be.

VALID_MATCH_HEADERS = [
    {'header': 'IN_PORT',
     'type': 'number',
     'min': 1,
     'max': 2**32-1,
     'mask': False,
     'prereqs': None},
    {'header': 'ETH_DST',
     'type': 'number',
     'min': 0,
     'max': 2**48-1,
     'mask': True,
     'prereqs': None},
    {'header': 'ETH_SRC',
     'type': 'number',
     'min': 0,
     'max': 2**48-1,
     'mask': True,
     'prereqs': None},
    {'header': 'ETH_TYPE',
     'type': 'number',
     'min': 0,
     'max': 2**16-1,
     'mask': False,
     'prereqs': None},
    {'header': 'IP_PROTO',
     'type': 'number',
     'min': 0,
     'max': 2**8-1,
     'mask': False,
     'prereqs': [ {'header': 'ETH_TYPE', 'value': 0x0800},
                  {'header': 'ETH_TYPE', 'value': 0x86dd} ]},
    {'header': 'IPV4_SRC',
     'type': 'IPAddress4',
     'mask': True,
     'prereqs': [ {'header': 'ETH_TYPE', 'value': 0x0800} ]},
    {'header': 'IPV4_DST',
     'type': 'IPAddress4',
     'mask': True,
     'prereqs': [ {'header': 'ETH_TYPE', 'value': 0x0800} ]},
    {'header': 'IPV6_SRC',
     'type': 'IPAddress6',
     'mask': True,
     'prereqs': [ {'header': 'ETH_TYPE', 'value': 0x86dd} ]},
    {'header': 'IPV6_DST',
     'type': 'IPAddress6',
     'mask': True,
     'prereqs': [ {'header': 'ETH_TYPE', 'value': 0x86dd} ]},
    {'header': 'TCP_SRC',
     'type': 'number'
     'min': 0,
     'max': 2**16-1,
     'mask': False,
     'prereqs': [ {'header': 'IP_PROTO', 'value': 6} ]},
    {'header': 'TCP_DST',
     'type': 'number'
     'min': 0,
     'max': 2**16-1,
     'mask': False,
     'prereqs': [ {'header': 'IP_PROTO', 'value': 6} ]},
    {'header': 'UDP_SRC',
     'type': 'number'
     'min': 0,
     'max': 2**16-1,
     'mask': False,
     'prereqs': [ {'header': 'IP_PROTO', 'value': 17} ]},
    {'header': 'UDP_DST',
     'type': 'number'
     'min': 0,
     'max': 2**16-1,
     'mask': False,
     'prereqs': [ {'header': 'IP_PROTO', 'value': 17} ]},
]

    
# For actions, a dictionary with the following fields will be used:
#    action    - Text definition of the action
#    fields    - List of dictionaries with the following fields
#        name      - Text identifier of the field. For instance: "port"
#        type      - See "type" in matches, uses the same types and additional
#                    dictionary entries for validation.
#        prereq    - Similar to "prereqs" in matches, names another field that,
#                    if set to the value provided, makes this a required field.
#                    This field is considered optional if prereq is not
#                    satisfied.
#            name      - Name of the field that's a prerequisite for this.
#            value     - Value of the field for this to be a non-optional field.
  
VALID_ACTIONS = [
    {'action': 'OUTPUT',
     'fields': [{'name': 'port',
                 'type': 'number',
                 'min': 1,
                 'max': 2**32-1},
                {'name': 'max_len',
                 'type': 'number',
                 'min': 0,
                 'max': OFPCML_MAX,
                 'other': OFPCML_NO_BUFFER,
                 'prereq': {'name': 'port', 'value': OFPP_CONTROLLER}}
                ]},
]
                
