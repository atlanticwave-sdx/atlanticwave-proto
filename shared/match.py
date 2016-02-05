# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project

from shared.ofconstants import *

OFM_NUMBER      = 1
OFM_BITMASK     = 2
OFM_IPV4        = 3
OFM_IPV6        = 4
OFM_PREFIX_V4   = 5
OFM_PREFIX_V6   = 6



class OpenFlowMatchTypeError(TypeError):
    pass

class OpenFlowMatchValueError(ValueError):
    pass

class OpenFlowMatchPrereqError(ValueError):
    pass



class OpenFlowMatch(object):
    ''' This class represents all the fields that are being matched at once.
        Its primary purpose is to hang on to the individual match elements and
        provide an easy way to verify if everything is valid and all 
        prerequisites are met. '''

    def __init__(self, fields):
        self.fields = field

    def check_validity(self):
        for field in self.fields:
            field.check_validity()

    def check_prerequisites(self):
        for field in self.fields:
            field.check_prerequisites(self.fields)


###### Below are OpenFlow Header Fields, for matching and modifying. #####

class IN_PORT(number_field):
    def __init__(self, value=None):
        super(IN_PORT, self).__init__('IN_PORT', value, min=1, max=OFPP_MAX)
        
class ETH_DST(number_field):
    def __init__(self, value=None, mask=False):
        super(ETH_DST, self).__init__('ETH_DST', value, min=0, max=2**48-1,
                                      mask=mask)

class ETH_SRC(number_field):
    def __init__(self, value=None, mask=False):
        super(ETH_SRC, self).__init__('ETH_SRC', value, min=0, max=2**48-1,
                                      mask=mask)

class ETH_TYPE(number_field):
    def __init__(self, value=None):
        super(ETH_TYPE, self).__init__('ETH_TYPE', value, min=0, max=2**16-1)

class IP_PROTO(number_field):
    def __init__(self, value=None):
        super(IP_PROTO, self).__init__('IP_PROTO', value, min=0, max=2**8-1,
                                       prereq=[ETH_TYPE(0x0800),
                                               ETH_TYPE(0x86dd)])

class IPV4_SRC(ipv4_field):
    def __init__(self, value=None, mask=False):
        super(IPV4_SRC, self).__init__('IPV4_SRC', value,
                                       prereq=[ETH_TYPE(0x0800)],
                                       mask=mask)

class IPV4_DST(ipv4_field):
    def __init__(self, value=None, mask=False):
        super(IPV4_DST, self).__init__('IPV4_DST', value,
                                       prereq=[ETH_TYPE(0x0800)],
                                       mask=mask)
        
class IPV6_SRC(ipv6_field):
    def __init__(self, value=None, mask=False):
        super(IPV6_SRC, self).__init__('IPV6_SRC', value,
                                       prereq=[ETH_TYPE(0x86dd)],
                                       mask=mask)

class IPV6_DST(ipv6_field):
    def __init__(self, value=None, mask=False):
        super(IPV6_DST, self).__init__('IPV6_DST', value,
                                       prereq=[ETH_TYPE(0x86dd)],
                                       mask=mask)

class TCP_SRC(number_field):
    def __init__(self, value=None):
        super(TCP_SRC, self).__init__('TCP_SRC', value, min=0, max=2**16-1,
                                      prereq=[IP_PROTO(6)])

class TCP_DST(number_field):
    def __init__(self, value=None):
        super(TCP_DST, self).__init__('TCP_DST', value, min=0, max=2**16-1,
                                      prereq=[IP_PROTO(6)])

class UDP_SRC(number_field):
    def __init__(self, value=None):
        super(UDP_SRC, self).__init__('UDP_SRC', value, min=0, max=2**16-1,
                                      prereq=[IP_PROTO(6)])

class UDP_DST(number_field):
    def __init__(self, value=None):
        super(UDP_DST, self).__init__('UDP_DST', value, min=0, max=2**16-1,
                                      prereq=[IP_PROTO(6)])





# This needs to be updated whenever there are new valid fields that we will
# accept.
VALID_MATCH_FIELDS = [ IN_PORT, ETH_DST, ETH_SRC, ETH_TYPE, IP_PROTO, IPV4_SRC,
                       IPV4_DST, IPV6_SRC, IPV6_DST, TCP_SRC, TCP_DST, UDP_SRC,
                       UDP_DST ]
