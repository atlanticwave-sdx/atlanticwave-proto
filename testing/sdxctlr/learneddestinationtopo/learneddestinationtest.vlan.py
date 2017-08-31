from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import custom
from mininet.node import RemoteController, Host
from mininet.cli import CLI

# This runs one switch, each with three hosts at easy to read formats.
# Each switch has its own separate controller.

# To run (in 3 separate terminals) the topology and two controllers.
#   cd ~/atlanticwave-proto/demo
#   sudo python demo-one-site.py
#
#   cd ~/atlanticwave-proto/sdxctlr
#   python SDXController.py
#
#   cd ~/atlanticwave-proto/
#   python LocalController.py
#

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

def LearnedDestinationSite():
    ''' This is the topology that we will be building here.

                            +-----+
                            | H1  |
                            +-----+
                              1|
                               |1
                            +-----+
               +------------+ SW1 +-------------+
               |          3 +-----+ 2           |
               |                                |
               |                                |
               |                                |
               | 2                            2 |
+-----+   1 +--+--+ 3                        +--+--+ 1    +-----+
| H3  +-----+ SW3 +--------------------------+ SW2 +------+ H2  |
+-----+ 1   +--+--+                        3 +--+--+    1 +-----+
             5 |  | 4                           | 4
               |  |                             |
               |  +--------------------------+  |
               |                             |  |
               | 2                         3 |  | 2
+-----+   1 +--+--+                          +--+--+ 1    +-----+
| H5  +-----+ SW5 +--------------------------+ SW4 +------+ H4  |
+-----+ 1   +--+--+ 3                     4  +--+--+    1 +-----+
               | 4                              | 5
               |                                |
               |                                |
               |          3 +-----+ 2           |
               +------------+ SW6 +-------------+
                            +-----+
                              1|
                               |1
                            +-----+
                            | H6  |
                            +-----+
'''


    # Hosts and switches
    net = Mininet(topo=None, build=False)
    sw1 = net.addSwitch('sw1', listenPort=6613, mac='00:00:00:00:00:01')
    sw2 = net.addSwitch('sw2', listenPort=6623, mac='00:00:00:00:00:02')
    sw3 = net.addSwitch('sw3', listenPort=6633, mac='00:00:00:00:00:03')
    sw4 = net.addSwitch('sw4', listenPort=6643, mac='00:00:00:00:00:04')
    sw5 = net.addSwitch('sw5', listenPort=6653, mac='00:00:00:00:00:05')
    sw6 = net.addSwitch('sw6', listenPort=6663, mac='00:00:00:00:00:06')

    h1 = net.addHost('h1', mac='00:00:00:00:01:00',
                     cls=VLANHost, vlan=1000)
    h2 = net.addHost('h2', mac='00:00:00:00:02:00',
                     cls=VLANHost, vlan=2000)
    h3 = net.addHost('h3', mac='00:00:00:00:03:00',
                     cls=VLANHost, vlan=1000)
    h4 = net.addHost('h4', mac='00:00:00:00:04:00',
                     cls=VLANHost, vlan=2000)
    h5 = net.addHost('h5', mac='00:00:00:00:05:00',
                     cls=VLANHost, vlan=1000)
    h6 = net.addHost('h6', mac='00:00:00:00:06:00',
                     cls=VLANHost, vlan=2000)

    # Wiring hosts
    net.addLink(h1, sw1, port1=1, port2=1)
    net.addLink(h2, sw2, port1=1, port2=1)
    net.addLink(h3, sw3, port1=1, port2=1)
    net.addLink(h4, sw4, port1=1, port2=1)
    net.addLink(h5, sw5, port1=1, port2=1)
    net.addLink(h6, sw6, port1=1, port2=1)

    # Wiring switches
    net.addLink(sw1, sw2, port1=2, port2=2)
    net.addLink(sw1, sw3, port1=3, port2=2)
    net.addLink(sw2, sw3, port1=3, port2=3)
    net.addLink(sw2, sw4, port1=4, port2=2)
    net.addLink(sw3, sw4, port1=4, port2=3)
    net.addLink(sw3, sw5, port1=5, port2=2)
    net.addLink(sw4, sw5, port1=4, port2=3)
    net.addLink(sw4, sw6, port1=5, port2=2)
    net.addLink(sw5, sw6, port1=4, port2=3)

    # Add controllers
    # https://stackoverflow.com/questions/23677291/how-to-connect-different-switches-to-different-remote-controllers-in-mininet

    sw1ctlr = net.addController('csw1', controller=RemoteController, 
                                ip='127.0.0.1', port=6613)
    sw2ctlr = net.addController('csw2', controller=RemoteController, 
                                ip='127.0.0.1', port=6623)
    sw3ctlr = net.addController('csw3', controller=RemoteController, 
                                ip='127.0.0.1', port=6633)
    sw4ctlr = net.addController('csw4', controller=RemoteController, 
                                ip='127.0.0.1', port=6643)
    sw5ctlr = net.addController('csw5', controller=RemoteController, 
                                ip='127.0.0.1', port=6653)
    sw6ctlr = net.addController('csw6', controller=RemoteController, 
                                ip='127.0.0.1', port=6663)

    
    net.build()
    print "net.build"
    
    sw1.start([sw1ctlr])
    sw2.start([sw2ctlr])
    sw3.start([sw3ctlr])
    sw4.start([sw4ctlr])
    sw5.start([sw5ctlr])
    sw6.start([sw6ctlr])
    #net.start()
    print "net.start"
    CLI(net)
    print "CLI(net)"
    net.stop()
    print "net.stop"


if __name__ == '__main__':
    LearnedDestinationSite()
