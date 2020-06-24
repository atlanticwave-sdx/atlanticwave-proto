from __future__ import absolute_import
# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project


from .LCFields import *


class SDXMatchTypeError(TypeError):
    pass

class SDXMatchValueError(ValueError):
    pass

class SDXMatch(object):
    ''' This is used to encapsulate matches for SDX Ingress and Egress policies.
        It uses LCFields to handle sanity checking of values.
    '''

    def __init__(self, name, value, field):
        ''' - name is the name of the field
            - value is the value that this particular field is initialized with
              and can be changed by setting the value.
            - field is an LCField.

            The field is created by the child of the SDXMatch. name and value 
            are likely duplicate, but here for ease-of-use.
        '''
        self._name = name
        self.value = value
        if not isinstance(field, LCField):
            raise SDXMatchTypeError("field is not LCField: %s" % type(field))
        self.field = field

    def __repr__(self):
        return "%s : %s:%s : %s" % (self.__class__.__name__,
                                    self._name,
                                    self.value,
                                    repr(self.field))

    def __str__(self):
        return str(self.field)

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return (self._name == other._name and
                self.value == other.value and
                self.field == other.field)

    def get_match(self):
        return self.field

    @staticmethod
    def lookup_match_type(name):
        if name not in SDXMATCH_TO_CLASS.keys():
            raise SDXMatchValueError("%s not in SDXMATCH_TO_CLASS: %s" %
                                     (name, SDXMATCH_TO_CLASS.keys()))
        return SDXMATCH_TO_CLASS[name]
                                
    

class SDXMatchSRCMAC(SDXMatch):
    def __init__(self, value):
        field = ETH_SRC(value)
        super(SDXMatchSRCMAC, self).__init__('SRCMAC', value, field)

class SDXMatchDSTMAC(SDXMatch):
    def __init__(self, value):
        field = ETH_DST(value)
        super(SDXMatchDSTMAC, self).__init__('DSTMAC', value, field)

class SDXMatchSRCIP(SDXMatch):
    def __init__(self, value):
        field = IPV4_SRC(value)
        super(SDXMatchSRCIP, self).__init__('SRCIP', value, field)

class SDXMatchDSTIP(SDXMatch):
    def __init__(self, value):
        field = IPV4_DST(value)
        super(SDXMatchDSTIP, self).__init__('DSTIP', value, field)

class SDXMatchTCPSRC(SDXMatch):
    def __init__(self, value):
        field = TCP_SRC(value)
        super(SDXMatchTCPSRC, self).__init__('TCPSRC', value, field)

class SDXMatchTCPDST(SDXMatch):
    def __init__(self, value):
        field = TCP_DST(value)
        super(SDXMatchTCPDST, self).__init__('TCPDST', value, field)

class SDXMatchUDPSRC(SDXMatch):
    def __init__(self, value):
        field = UDP_SRC(value)
        super(SDXMatchUDPSRC, self).__init__('UDPSRC', value, field)

class SDXMatchUDPDST(SDXMatch):
    def __init__(self, value):
        field = UDP_DST(value)
        super(SDXMatchUDPDST, self).__init__('UDPDST', value, field)

class SDXMatchIPPROTO(SDXMatch):
    def __init__(self, value):
        field = IP_PROTO(value)
        super(SDXMatchIPPROTO, self).__init__('IPPROTO', value, field)

class SDXMatchETHTYPE(SDXMatch):
    def __init__(self, value):
        field = ETH_TYPE(value)
        super(SDXMatchETHTYPE, self).__init__('ETHTYPE', value, field)

class SDXMatchVLAN(SDXMatch):
    def __init__(self, value):
        field = VLAN_VID(value)
        super(SDXMatchVLAN, self).__init__('VLAN', value, field)

        


SDXMATCH_TO_CLASS = {
    'src_mac':SDXMatchSRCMAC,
    'dst_mac':SDXMatchDSTMAC,
    'src_ip':SDXMatchSRCIP,
    'dst_ip':SDXMatchDSTIP,
    'tcp_src':SDXMatchTCPSRC,
    'tcp_dst':SDXMatchTCPDST,
    'udp_src':SDXMatchTCPSRC,
    'udp_dst':SDXMatchTCPDST,
    'ip_proto':SDXMatchIPPROTO,
    'eth_type':SDXMatchETHTYPE,
    'vlan':SDXMatchVLAN
}

