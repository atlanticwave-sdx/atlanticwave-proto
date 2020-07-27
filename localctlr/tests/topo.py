from __future__ import unicode_literals
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController

# Single switch for testing.


class OneSwitch(Topo):

    def __init__(self, **params):
        Topo.__init__(self, **params)

        sw = self.addSwitch('s1', mac='00:00:00:00:00:01')
        h1 = self.addHost('h1', mac='00:00:00:00:01:00')
        h2 = self.addHost('h2', mac='00:00:00:00:02:00')

        self.addLink(h1, sw)
        self.addLink(h2, sw)

if __name__ == '__main__':
    topo = OneSwitch()

    net = Mininet(topo=topo, build=False)

    net.addController(controller=RemoteController,
                      ip='127.0.0.1', port=6633)
    net.build()
    net.start()
    CLI(net)
