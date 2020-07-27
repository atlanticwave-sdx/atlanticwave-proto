from __future__ import print_function
from mininet.topo import Topo
from mininet.net import Containernet
from mininet.link import TCLink
from mininet.util import custom
from mininet.node import RemoteController, Host
from mininet.cli import CLI

from docker.types import Mount
import sys

# This runs multiple switch, each with three hosts at easy to read formats.
# LAX and NYC have their own Local Controllers, while ORD and ATL share a
# single local controller

# To run (in 3 separate terminals) the topology and two controllers.
#   cd ~/atlanticwave-proto/demo
#   sudo python demo-multi-site.py
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

def MultiSite(dir):
    ''' This is the topology that we will be building here.



                             21         22        23
                         +-------+  +-------+  +-------+
                         | ORDH1 |  | ORDH2 |  | ORDH3 |
                         +---+---+  +---+---+  +---+---+
                           1 |        2 |        3 |
                             |   1      | 2        | 3
                             +------+---+---+------+
                                    | ORDS1 |
                           +--------+---+---+-----+
 VLAN          PORT        |       4    |     6   |
     +-------+ 1           |            | 5       |          1 +-------+
 11  | LAXH1 +-----+       |            |         |       +----+ NYCH1 | 31
     +-------+   1 |       |            |         |       | 1  +-------+
                   |       |4           |       4 |       |
     +-------+ 2   +-------+            |         +-------+  2 +-------+
 12  | LAXH2 +-----+ LAXS1 |            |         | NYCS1 +----+ NYCH2 | 32
     +-------+   2 +-------+            |         +---+---+ 2  +-------+
                   | 10|   |5           |          10 |   |
     +-------+ 3   |   |   |            |             |   |  3 +-------+
 13  | LAXH3 +-----+   |   |            |             |   +----+ NYCH3 | 33
     +-------+   3     |   |            |             |     3  +-------+
                       |   |            |             |
        +--------+     |   |            | 5           |   +--------+
  .100  | WESTLC +-----+   |      4     |             +---+ EASTLC |.102
        +--------+         +--------+---+---+             +--------+
                                    |       |
                    +--------+   10 |       | 11   +----------+
              .101  | CENTLC +------+ ATLS1 +------+ SDX CTLR |.200
                    +--------+      |       |      +----------+
                                    |       |
                             +------+-------+------+
                             |  1       |2         | 3
                            1|         2|         3|
                         +-------+  +-------+  +-------+
                         | ATLH1 |  | ATLH2 |  | ATLH3 |
                         +-------+  +-------+  +-------+
                            41          42        43

'''


    # Hosts and switches
    net = Containernet(topo=None, build=False)
    laxswitch = net.addSwitch('s1', listenPort=6680, mac='00:00:00:00:00:01')
    ordswitch = net.addSwitch('s2', listenPort=6681, mac='00:00:00:00:00:02')
    nycswitch = net.addSwitch('s3', listenPort=6682, mac='00:00:00:00:00:03')
    atlswitch = net.addSwitch('s4', listenPort=6681, mac='00:00:00:00:00:04')

    laxh1 = net.addHost('laxh1', mac='00:00:00:00:11:00',
                        cls=VLANHost, vlan=11)
    laxh2 = net.addHost('laxh2', mac='00:00:00:00:12:00',
                        cls=VLANHost, vlan=12)
    laxh3 = net.addHost('laxh3', mac='00:00:00:00:13:00',
                        cls=VLANHost, vlan=13)
    ordh1 = net.addHost('ordh1', mac='00:00:00:00:21:00',
                        cls=VLANHost, vlan=21)
    ordh2 = net.addHost('ordh2', mac='00:00:00:00:22:00',
                        cls=VLANHost, vlan=22)
    ordh3 = net.addHost('ordh3', mac='00:00:00:00:23:00',
                        cls=VLANHost, vlan=23)
    nych1 = net.addHost('nych1', mac='00:00:00:00:31:00',
                        cls=VLANHost, vlan=31)
    nych2 = net.addHost('nych2', mac='00:00:00:00:32:00',
                        cls=VLANHost, vlan=32)
    nych3 = net.addHost('nych3', mac='00:00:00:00:33:00',
                        cls=VLANHost, vlan=33)
    atlh1 = net.addHost('atlh1', mac='00:00:00:00:41:00',
                        cls=VLANHost, vlan=41)
    atlh2 = net.addHost('atlh2', mac='00:00:00:00:42:00',
                        cls=VLANHost, vlan=42)
    atlh3 = net.addHost('atlh3', mac='00:00:00:00:43:00',
                        cls=VLANHost, vlan=43)

    # Controller containers
    sdx_env = {"MANIFEST":"/development/configuration/containernet-vagrant/containernet.manifest",
               "IPADDR":"0.0.0.0", "PORT":"5000", "LCPORT":"5555",
               "PYTHONPATH":".:/development/", "AWAVEDIR":"/development"}
    sdx_pbs = {5000:5000}
    sdx_volumes = [dir + ":/development:rw"]
    sdx_cmd = "/run_sdx.sh"
    sdxctlr = net.addDocker('sdx', ip='192.168.0.200', dimage="sdx_container",
                            environment=sdx_env, port_bindings=sdx_pbs,
                            volumes=sdx_volumes, dcmd=sdx_cmd)
                            #volumes=sdx_volumes)
    
    westlc_env = {"MANIFEST":"/development/configuration/containernet-vagrant/containernet.manifest",
                  "SITE":"westctlr", "PYTHONPATH":".:/development/",
                  "SDXIP":"192.168.0.200", "AWAVEDIR":"/development"}

    westlc_pbs = {6680:6680}
    westlc_volumes = sdx_volumes
    westlc_cmd = "/run_lc.sh"
    westlc = net.addDocker('westctlr', ip='192.168.0.100',
                           dimage="lc_container",
                           environment=westlc_env, port_bindings=westlc_pbs,
                           volumes=westlc_volumes, dcmd=westlc_cmd)
                           #volumes=westlc_volumes)
                           
    centlc_env = {"MANIFEST":"/development/configuration/containernet-vagrant/containernet.manifest",
                  "SITE":"centctlr", "PYTHONPATH":".:/development/",
                  "SDXIP":"192.168.0.200", "AWAVEDIR":"/development"}
    centlc_pbs = {6681:6681}
    centlc_volumes = sdx_volumes
    centlc_cmd = "/run_lc.sh"
    centlc = net.addDocker('centctlr', ip='192.168.0.101',
                           dimage="lc_container",
                           environment=centlc_env, port_bindings=centlc_pbs,
                           volumes=centlc_volumes, dcmd=centlc_cmd)
                           #volumes=centlc_volumes)
    
    eastlc_env = {"MANIFEST":"/development/configuration/containernet-vagrant/containernet.manifest",
                  "SITE":"eastctlr", "PYTHONPATH":".:/development/",
                  "SDXIP":"192.168.0.200", "AWAVEDIR":"/development"}
    eastlc_pbs = {6682:6682}
    eastlc_volumes = sdx_volumes
    eastlc_cmd = "/run_lc.sh"
    eastlc = net.addDocker('eastctlr', ip='192.168.0.102',
                           dimage="lc_container",
                           environment=eastlc_env, port_bindings=eastlc_pbs,
                           volumes=eastlc_volumes, dcmd=eastlc_cmd)
                           #volumes=eastlc_volumes)


    # Host Wiring
    net.addLink(laxswitch, laxh1, port1=1)
    net.addLink(laxswitch, laxh2, port1=2)
    net.addLink(laxswitch, laxh3, port1=3)
    net.addLink(ordswitch, ordh1, port1=1)
    net.addLink(ordswitch, ordh2, port1=2)
    net.addLink(ordswitch, ordh3, port1=3)
    net.addLink(nycswitch, nych1, port1=1)
    net.addLink(nycswitch, nych2, port1=2)
    net.addLink(nycswitch, nych3, port1=3)
    net.addLink(atlswitch, atlh1, port1=1)
    net.addLink(atlswitch, atlh2, port1=2)
    net.addLink(atlswitch, atlh3, port1=3)


    # Switch Wiring
    net.addLink(laxswitch, ordswitch, port1=4, port2=4)
    net.addLink(laxswitch, atlswitch, port1=5, port2=4)
    net.addLink(ordswitch, atlswitch, port1=5, port2=5)
    net.addLink(ordswitch, nycswitch, port1=6, port2=4)

    # Controller wiring
    net.addLink(laxswitch, westlc, port1=10)
    net.addLink(atlswitch, centlc, port1=10)
    net.addLink(atlswitch, sdxctlr, port1=11)
    net.addLink(nycswitch, eastlc, port1=10)

    # Add controllers
    # https://stackoverflow.com/questions/23677291/how-to-connect-different-switches-to-different-remote-controllers-in-mininet
    #FIXME: Check these IPs!
    westctlr = net.addController('c1', controller=RemoteController, 
                                 ip='172.17.0.3', port=6680)
    centctlr = net.addController('c2', controller=RemoteController, 
                                 ip='172.17.0.4', port=6681)
    eastctlr = net.addController('c3', controller=RemoteController, 
                                 ip='172.17.0.5', port=6682)
    net.build()
    print("net.build")
    laxswitch.start([westctlr])
    ordswitch.start([centctlr])
    nycswitch.start([eastctlr])
    atlswitch.start([centctlr])
    
    #net.start()
    print("net.start")
    CLI(net)
    print("CLI(net)")
    net.stop()
    print("net.stop")


if __name__ == '__main__':
    print("USAGE: python containernet-mn-topo.py </absolute/path/to/local/AWave/directory>")
    print("    Path is optional")
    dir = "/home/ubuntu/dev"
    if len(sys.argv) > 1:
        dir = sys.argv[1]
    MultiSite(dir)
