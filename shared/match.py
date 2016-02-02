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
    ''' This is the parent class for all OpenFlow Matches. It will include
        much of the functionality built-in that is necessary to validate 
        most matches, including how to validate number, IP address, etc.
        Subclasses will need to fill in certain values defined in __init__()
        which will often be enough for the existing validation routines. '''

    def __init__(self, value, mask=False):
         self.value = value
         self.mask = mask

         # MANDATORY: The type is the style of the value that is being used.
         # It can be OFM_NUMBER, OFM_BITMASK, OFM_IPV4, OFM_IPV6, OFM_PREFIX_V4,
         # or OFM_PREFIX_V6
         self.type = None
         
         # MANDATORY: If there are prerequisites, they must be listed here.
         # This is a list of tuples where if any of the conditions are
         # satisfied, the prerequisites are fufilled. The tuples are a
         # (type, value), which must also be in the match list. These are
         # checked by check_prerequisites().
         # Most matches do not have prerequisites. 
         self.prereqs = None

         # If self.type == OFM_NUMBER, the following values must be filled out.
         # other is optional, leaving at None is when it is not necessary.
         # If the value must be betten 0-65530 *or* 65535,
         #    min = 0, max = 65530, other = 65535.
         self.min = None
         self.max = None
         self.other = None

         # If self.type == OFM_BITMASK, the following must be filled out.
         self.bitmin = None
         self.bitmax = None

         # If self.type == OFM_IPV4, OFM_IPV6, OFM_PREFIX_V4, or OFM_PREFIX_V6
         # a special validation routine will be used.

         # This private value is set to True if self.check_validity() passes.
         # It's used to optimize the validity checking during
         # self.check_prerequisites().
         self._valid = False

         
    def check_validity(self):
        ''' Checks the validity of self.value. It does not check the validity of
            the prerequisites. '''

        if self._valid:
            return
        
        if self.type == OFM_NUMBER:
            self._check_number_validity()
        elif self.type == OFM_BITMASK:
            self._check_bitmask_validity()
        elif self.type == OFM_IPV4:
            self._check_IPv4_validity()
        elif self.type == OFM_IPV6:
            self._check_IPv6_validity()
        elif self.type == OFM_PREFIX_V4:
            self._check_v4prefix_validity()
        elif self.type == OFM_PREFIX_V6:
            self._check_v6prefix_validity()

        self._valid = True
            
    def _check_number_validity(self):
        # Check if self.value is a number
         if not isinstance(self.value, int):
             raise OpenFlowMatchTypeError("self.value is not of type int")

         # Check if self.value is between self.min and self.max a
         if self.value < min or self.value > max:
             if self.other is not None:
                 raise OpenFlowMatchValueError(
                     "self.value is not between " + str(self.min) +
                     " and " + str(self.max))
             elif self.value not in self.other:
                 raise OpenFlowMatchValueError(
                     "self.value is not between " + str(self.min) +
                     " and " + str(self.max) + " and not in (" +
                     str(self.others) + ")")


    def _check_bitmask_validity(self):
        # Check if self.value is a number
         if not isinstance(self.value, int):
             raise OpenFlowMatchTypeError("self.value is not of type int")

        # Check if self.value is between self.min and self.max
        if self.value < min or self.value > max:
            raise OpenFlowMatchValueError(
                "self.value is not between " + str(self.min) +
                " and " + str(self.max))

    def _check_IPv4_validity(self):
        pass

    def _check_IPv6_validity(self):
        pass

    def _check_v4prefix_validity(self):
        pass

    def _check_v6prefix_validity(self):
        pass

    def check_prerequisites(self, allmatches):
        if self.prereqs == None:
            return
        # Loop through each match
        for match in allmatches:
            # On each match, check if a prerequisite is covered.
            for prereq_type, prereq_val  in self.prereqs:
                if type(match) == prereq_type:
                    if match.value == prereq_val:
                        # Check if this prereq is also valid and satisfied.
                        try:
                            match.check_validity()
                        except OpenFlowMatchTypeError, OpenFlowMatchValueError:
                            raise 

                        try:
                            match.check_prerequisites(allmatches)
                        except OpenFlowMatchPrereqError:
                            raise
                        # If it's gotten this far, this is good news. Return.
                        return

        # If it's gotten this far, that means the prereqs haven't been met.
        # Time to raise an OpenFlowPrereqError.
        raise OpenFlowMatchPrereqError("Prerequisites for " +
                                       str(self.__class__.__name__) +
                                       " have not been met.")



class match_IN_PORT(OpenFlowMatch):
    def __init__(self, value):
        super(match_IN_PORT, self).__init__(value)

        self.type = OFM_NUMBER
        self.min = 1
        self.max = OFPP_MAX
        self.others = [OFPP_IN_PORT, OFPP_TABLE, OFPP_NORMAL, OFPP_FLOOD,
                       OFPP_ALL, OFPP_CONTROLLER, OFPP_LOCAL, OFPP_ANY]

class match_ETH_DST(OpenFlowMatch):
    def __init__(self, value, mask):
        super(match_ETH_DST, self).__init__(value, mask)

        self.type = OFM_NUMBER
        self.min = 0
        self.max = 2**48-1

class match_ETH_SRC(OpenFlowMatch):
    def __init__(self, value, mask):
        super(match_ETH_SRC, self).__init__(value, mask)

        self.type = OFM_NUMBER
        self.min = 0
        self.max = 2**48-1

class match_ETH_TYPE(OpenFlowMatch):
    def __init__(self, value):
        super(match_ETH_TYPE, self).__init__(value)

        self.type = OFM_NUMBER
        self.min = 0
        self.max = 2**16-1

class match_IP_PROTO(OpenFlowMatch):
    def __init__(self, value):
        super(match_IP_PROTO, self).__init__(value)

        self.type = OFM_NUMBER
        self.min = 0
        self.max = 2**8-1
        self.prereqs = [ (match_ETH_TYPE, 0x0800),
                         (match_ETH_TYPE, 0x86dd) ]
        
class match_IPV4_SRC(OpenFlowMatch):
    def __init__(self, value, mask):
        super(match_IPV4_SRC, self).__init__(value, mask)

        self.type = OFM_IPV4
        self.prereqs = [ (match_ETH_TYPE, 0x0800) ]

class match_IPV4_DST(OpenFlowMatch):
    def __init__(self, value, mask):
        super(match_IPV4_DST, self).__init__(value, mask)

        self.type = OFM_IPV4
        self.prereqs = [ (match_ETH_TYPE, 0x0800) ]

class match_IPV6_SRC(OpenFlowMatch):
    def __init__(self, value, mask):
        super(match_IPV6_SRC, self).__init__(value, mask)

        self.type = OFM_IPV6
        self.prereqs = [ (match_ETH_TYPE, 0x86dd) ]

class match_IPV6_DST(OpenFlowMatch):
    def __init__(self, value, mask):
        super(match_IPV6_DST, self).__init__(value, mask)

        self.type = OFM_IPV6
        self.prereqs = [ (match_ETH_TYPE, 0x86dd) ]
         
class match_TCP_SRC(OpenFlowMatch):
    def __init__(self, value):
        super(match_TCP_SRC, self).__init__(value)

        self.type = OFM_NUMBER
        self.min = 0
        self.max = 2**16-1
        self.prereqs = [ (match_IP_PROTO, 6) ]

class match_TCP_DST(OpenFlowMatch):
    def __init__(self, value):
        super(match_TCP_DST, self).__init__(value)

        self.type = OFM_NUMBER
        self.min = 0
        self.max = 2**16-1
        self.prereqs = [ (match_IP_PROTO, 6) ]

class match_UDP_SRC(OpenFlowMatch):
    def __init__(self, value):
        super(match_UDP_SRC, self).__init__(value)

        self.type = OFM_NUMBER
        self.min = 0
        self.max = 2**16-1
        self.prereqs = [ (match_IP_PROTO, 17) ]

class match_UDP_DST(OpenFlowMatch):
    def __init__(self, value):
        super(match_UDP_DST, self).__init__(value)

        self.type = OFM_NUMBER
        self.min = 0
        self.max = 2**16-1
        self.prereqs = [ (match_IP_PROTO, 17) ]
