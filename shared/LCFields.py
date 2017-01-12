# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import sys
from netaddr import EUI, IPAddress
from shared.ofconstants import *


class LCFieldTypeError(TypeError):
    pass

class LCFieldValueError(ValueError):
    pass

class LCFieldPrereqError(ValueError):
    pass

class LCField(object):
    ''' This is the parent class for different kinds of fields that are used in
        FCActions (defined below). It provides common structure and 
        defines descriptors for each child class. '''
    
    def __init__(self, name, value=None, mask=False, prereqs=None):
        ''' - name is the name of the field
            - value is the value that this particular field is initialized with
              and can be changed by setting the value.
            - mask is a mask value, if that's appropriate for a particular field
            - prereqs are fields that must be matched upon before matching on 
              this particular field. For example, IPv4 addresses cannot be 
              matched unless the ETH_TYPE is set to 0x0800. These will used by
              the translator primarily, and there's no need for users to include
              these fields in their "match" statements.
        '''
        
        self._name = name
        self.value = value
        self.mask = mask
        self.prereqs = prereqs

    def __repr__(self):
        return "%s : %s:%s %s" % (self.__class__.__name__,
                                  self._name,
                                  self.value,
                                  self.mask)

    def __str__(self):
        retstr = "%s:%s" % (self._name, self.value)
        if self.mask != False:
            retstr += " %s" % self.mask
        return retstr

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return (self._name == other._name and
                self.value == other.value and
                self.mask == other.mask)
        
    #TODO - Can these be represented as a property/discriptor? I don't think so.
    def get(self):
        return self.value

    def set(self, value):
        self.value = value

    def get_mask(self):
        return self.mask

    def set_mask(self, mask):
        self.mask = mask

    def get_name(self):
        return self._name

    def get_prereqs(self):
        return self.prereqs

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if ((self._name == other._name) and
            (self.value == other.value)):
            return True
        return False

    def check_validity(self):
        raise NotImplementedError("Subclasses must implement this.")


class number_field(LCField):
    ''' Used for fields that need to be numbers. Has additional required init
        fields:
            minval - Minimum value that is allowed.
            maxval - Maximum value that is allowed.
            others - Optional field that is a list of other values that are
                     valid.
    '''
    def __init__(self, name, minval, maxval, value=None, mask=False, others=[]):
        if value is not None:
            if type(value) is not int and type(value) is not long:
                raise LCFieldTypeError("value is not a number")
        
        self.minval = minval
        self.maxval = maxval
        self.others = others

        super(number_field, self).__init__(name, value)


    def check_validity(self):
        # Check if self.value is a number
        if not isinstance(self.value, int):
            raise LCFieldTypeError("self.value of " + self._name + " is not of type int: " + str(type(self.value)))

        # Check if self.value is between self.minval and self.maxval
        if (self.value < self.minval) or (self.value > self.maxval):
             if len(self.others) == 0 :
                 raise LCFieldValueError(
                     "self.value (" + str(self.value) + ") is not between " + str(self.minval) +
                     " and " + str(self.maxval))
             elif self.value not in self.others:
                 raise LCFieldValueError(
                     "self.value is not between " + str(self.minval) +
                     " and " + str(self.maxval) + " and not in (" +
                     str(self.others) + ")")        


class bitmask_field(number_field):
    ''' Used for fields that need bitmasks. Same as a number_field right 
        now, but could change in the future. '''
    pass

class mac_field(number_field):
    ''' Used for MAC address fields. '''
    def __init__(self, name, value=None, mask=False):
        if value is not None:
            mac = EUI(value)

        super(mac_field, self).__init__(name, value=int(mac), 
                                        minval=0, maxval=2**48-1,
                                        mask=mask)


class ipv4_field(number_field):
    ''' Used for IPv4 addresses. '''
    def __init__(self, name, value=None, mask=False):
        if value is not None:
            ip = IPAddress(value)

        super(ipv4_field, self).__init__(name, value=int(ip),
                                         minval=0, maxval=2**32-1,
                                         mask=mask)

    def __str__(self):
        retstr = "%s:%s" % (self._name, IPAddress(self.value))
        return retstr



class ipv6_field(number_field):
    ''' Used for IPv6 addresses. '''
    def __init__(self, name, value=None, mask=False):
        if value is not None:
            ip = IPAddress(value, 6)

        super(ipv6_field, self).__init__(name, value=int(ip),
                                         minval=0, maxval=2**128-1,
                                         mask=mask)
    def __str__(self):
        retstr = "%s:%s" % (self._name, IPAddress(self.value, 6))
        return retstr





###### Below are fields that can be sent from the SDXController to the 
###### LocalController and be properly interpreted
class IN_PORT(number_field):
    def __init__(self, value=None):
        super(IN_PORT, self).__init__('in_port', value=value,
                                      minval=1, maxval=OFPP_MAX)
        
class ETH_DST(mac_field):
    def __init__(self, value=None, mask=False):
        super(ETH_DST, self).__init__('eth_dst', value=value,
                                      mask=mask)

class ETH_SRC(mac_field):
    def __init__(self, value=None, mask=False):
        super(ETH_SRC, self).__init__('eth_src', value=value,
                                      mask=mask)

class ETH_TYPE(number_field):
    def __init__(self, value=None):
        super(ETH_TYPE, self).__init__('eth_type', value=value,
                                       minval=0, maxval=2**16-1)

class IP_PROTO(number_field):
    def __init__(self, value=None):
        super(IP_PROTO, self).__init__('ip_proto', value=value,
                                       minval=0, maxval=2**8-1,
                                       prereq=[ETH_TYPE(0x0800)])
        #FIXME: The prereq is only for IPv4. Need to figure out how to support
        # IPv6 with this.

class IPV4_SRC(ipv4_field):
    def __init__(self, value=None, mask=False):
        super(IPV4_SRC, self).__init__('ipv4_src', value=value,
                                       mask=mask,
                                       prereq=[ETH_TYPE(0x0800)])

class IPV4_DST(ipv4_field):
    def __init__(self, value=None, mask=False):
        super(IPV4_DST, self).__init__('ipv4_dst', value=value,
                                       mask=mask,
                                       prereq=[ETH_TYPE(0x0800)])
        
#class IPV6_SRC(ipv6_field):
#    def __init__(self, value=None, mask=False):
#        super(IPV6_SRC, self).__init__('ipv6_src', value=value,
#                                       mask=mask,
#                                       prereq=[ETH_TYPE(0x86dd)])

#class IPV6_DST(ipv6_field):
#    def __init__(self, value=None, mask=False):
#        super(IPV6_DST, self).__init__('ipv6_dst', value=value,
#                                       mask=mask,
#                                       prereq=[ETH_TYPE(0x86dd)])

class TCP_SRC(number_field):
    def __init__(self, value=None):
        super(TCP_SRC, self).__init__('tcp_src', value=value,
                                      minval=0, maxval=2**16-1,
                                      prereq=[IP_PROTO(6),
                                              ETH_TYPE(0x0800)])

class TCP_DST(number_field):
    def __init__(self, value=None):
        super(TCP_DST, self).__init__('tcp_dst', value=value,
                                      minval=0, maxval=2**16-1,
                                      prereq=[IP_PROTO(6),
                                              ETH_TYPE(0x0800)])

class UDP_SRC(number_field):
    def __init__(self, value=None):
        super(UDP_SRC, self).__init__('udp_src', value=value,
                                      minval=0, maxval=2**16-1,
                                      prereq=[IP_PROTO(17),
                                              ETH_TYPE(0x0800)])

class UDP_DST(number_field):
    def __init__(self, value=None):
        super(UDP_DST, self).__init__('udp_dst', value=value,
                                      minval=0, maxval=2**16-1,
                                      prereq=[IP_PROTO(17),
                                              ETH_TYPE(0x0800)])

class VLAN_VID(number_field):
    # FIXME: Perhaps this should be changed from a number_field to something
    # new, like a vlan_field that can handle the 12+1 bits that VLANs need?
    def __init__(self, value, cfi=1, mask=False):
        # Adjust for the CFI bit. maxval is also adjusted for this.
        self.cfi = cfi
        value = value + (0x1000*cfi)
        super(VLAN_VID, self).__init__('vlan_vid', value=value,
                                       minval=0, maxval=2**13-1,
                                       mask=mask)
    def __str__(self):
        retstr = "%s:%s,%s" % (self._name,
                               (self.value - (0x1000*self.cfi)), # Actual VLAN
                               self.cfi)
        return retstr



# This needs to be updated whenever there are new valid fields that we will
# accept.
VALID_MATCH_FIELDS = [ IN_PORT, ETH_DST, ETH_SRC, ETH_TYPE, IP_PROTO, IPV4_SRC,
                       IPV4_DST, TCP_SRC, TCP_DST, UDP_SRC,
                       UDP_DST, VLAN_VID ]


# This is a translation mechanism for mapping a name to a class
# Value is assumed
# Can be used for aliases!
#FIXME: is this necessary?
MATCH_NAME_TO_CLASS = { 'in_port': {'type':IN_PORT, 'required':None},
                        'eth_dst': {'type':ETH_DST, 'required':['mask']},
                        'eth_src': {'type':ETH_SRC, 'required':['mask']},
                        'eth_type': {'type':ETH_TYPE, 'required':None},
                        'ip_proto': {'type':IP_PROTO, 'required':None},
                        'ipv4_src': {'type':IPV4_SRC, 'required':['mask']},
                        'ipv4_dst': {'type':IPV4_DST, 'required':['mask']},
#                        'ipv6_src': {'type':IPV6_SRC, 'required':['mask']},
#                        'ipv6_dst': {'type':IPV6_DST, 'required':['mask']},
                        'tcp_src': {'type':TCP_SRC, 'required':None},
                        'tcp_dst': {'type':TCP_DST, 'required':None},
                        'udp_src': {'type':UDP_SRC, 'required':None},
                        'udp_dst': {'type':UDP_DST, 'required':None},
                        'vlan_vid': {'type':VLAN_VID, 'required':None},
                       }
