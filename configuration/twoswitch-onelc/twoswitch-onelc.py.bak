from __future__ import print_function
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import custom
from mininet.node import RemoteController, Host
from mininet.cli import CLI

# This runs one switch, each with three hosts at easy to read formats.
# Both switches share a single LC

# From: https://github.com/mininet/mininet/blob/master/examples/vlanhost.py

class VLANHost( Host ):
    "Host connected to VLAN interface"

    def config( self, vlan=100, **params ):
        """Configure VLANHost according to (optional) parameters:
           vlan: VLAN ID for default interface"""

        r = super( VLANHost, self ).config( **params )

        intf = self.defaultIntf()
        # remove IP from default, "physical" interface
        self.cmd( 'ifconfig %s inet 0' % intf )
        # create VLAN interface
        self.cmd( 'vconfig add %s %d' % ( intf, vlan ) )
        # assign the host's IP to the VLAN interface
        self.cmd( 'ifconfig %s.%d inet %s' % ( intf, vlan, params['ip'] ) )
        # update the intf name and host's intf map
        newName = '%s.%d' % ( intf, vlan )
        # update the (Mininet) interface to refer to VLAN interface name
        intf.name = newName
        # add VLAN interface to host's name to intf map
        self.nameToIntf[ newName ] = intf

        return r

hosts = { 'vlan': VLANHost }

def TwoSwitchOneLC():
    ''' This is the topology that we will be building here.
VLAN+------+1      1                             1       1+------+
1234|  ATL +-------+                             +--------+ MIA  |1234
    +------+       +----------+ 3   3 +----------+        +------+
                   | Switch 1 +-------+ Switch 2 |
    +------+       +----------+       +----------+        +------+
2345|ATLDTN+-------+                             +--------+MIADTN|2345
    +------+1      2                             2       1+------+

'''


    # Hosts and switches
    net = Mininet(topo=None, build=False)
    switch1 = net.addSwitch('s1', listenPort=6681, mac='00:00:00:00:00:01')
    switch2 = net.addSwitch('s2', listenPort=6682, mac='00:00:00:00:00:02')

    atl    = net.addHost('atl', mac='00:00:00:00:01:00',
                         cls=VLANHost, vlan=1234)
    atldtn = net.addHost('atldtn', mac='00:00:00:00:02:00',
                         cls=VLANHost, vlan=2345)                         

    mia    = net.addHost('miah1', mac='00:00:00:00:03:00',
                         cls=VLANHost, vlan=1234)
    miadtn = net.addHost('miah2', mac='00:00:00:00:04:00',
                         cls=VLANHost, vlan=2345)

    # Wiring
    net.addLink(switch1, atl, port1=1)
    net.addLink(switch1, atldtn, port1=2)
    net.addLink(switch2, mia, port1=1)
    net.addLink(switch2, miadtn, port1=2)
    net.addLink(switch1, switch2, port1=3, port2=3)

    # Add controller
    # https://stackoverflow.com/questions/23677291/how-to-connect-different-switches-to-different-remote-controllers-in-mininet

    atlctlr = net.addController('c0', controller=RemoteController, 
                                ip='127.0.0.1', port=6680)
    
    net.build()
    print("net.build")
    
    net.start()
    print("net.start")
    CLI(net)
    print("CLI(net)")
    net.stop()
    print("net.stop")


if __name__ == '__main__':
    TwoSwitchOneLC()
