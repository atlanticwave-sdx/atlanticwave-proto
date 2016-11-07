""" RNP topology
    Data source: https://rnp.br/servicos/conectividade/trafego
    Heavily modified by Sean Donovan for AtlanticWave/SDX project demonstration
"""
from mininet.topo import Topo
from mininet.node import RemoteController,Host
from mininet.cli import CLI
from mininet.net import Mininet

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

class MyTopo():
    net = Mininet(topo=None, build=False)
    
    # Add switches
    acSw = net.addSwitch('sw1', listenport=6601, mac='00:00:00:00:00:01')
    alSw = net.addSwitch('sw2', listenport=6602, mac='00:00:00:00:00:02')
    apSw = net.addSwitch('sw3', listenport=6603, mac='00:00:00:00:00:03')
    amSw = net.addSwitch('sw4', listenport=6604, mac='00:00:00:00:00:04')
    baSw = net.addSwitch('sw5', listenport=6605, mac='00:00:00:00:00:05')
    ceSw = net.addSwitch('sw6', listenport=6606, mac='00:00:00:00:00:06')
    dfSw = net.addSwitch('sw7', listenport=6607, mac='00:00:00:00:00:07')
    esSw = net.addSwitch('sw8', listenport=6608, mac='00:00:00:00:00:08')
    goSw = net.addSwitch('sw9', listenport=6609, mac='00:00:00:00:00:09')
    maSw = net.addSwitch('sw10', listenport=6610, mac='00:00:00:00:00:10')
    mtSw = net.addSwitch('sw11', listenport=6611, mac='00:00:00:00:00:11')
    msSw = net.addSwitch('sw12', listenport=6612, mac='00:00:00:00:00:12')
    mgSw = net.addSwitch('sw13', listenport=6613, mac='00:00:00:00:00:13')
    paSw = net.addSwitch('sw14', listenport=6614, mac='00:00:00:00:00:14')
    pbjSw = net.addSwitch('sw15', listenport=6615, mac='00:00:00:00:00:15')
    prSw = net.addSwitch('sw16', listenport=6616, mac='00:00:00:00:00:16')
    peSw = net.addSwitch('sw17', listenport=6617, mac='00:00:00:00:00:17')
    piSw = net.addSwitch('sw18', listenport=6618, mac='00:00:00:00:00:18')
    rjSw = net.addSwitch('sw19', listenport=6619, mac='00:00:00:00:00:19')
    rnSw = net.addSwitch('sw20', listenport=6620, mac='00:00:00:00:00:20')
    rsSw = net.addSwitch('sw21', listenport=6621, mac='00:00:00:00:00:21')
    roSw = net.addSwitch('sw22', listenport=6622, mac='00:00:00:00:00:22')
    rrSw = net.addSwitch('sw23', listenport=6623, mac='00:00:00:00:00:23')
    scSw = net.addSwitch('sw24', listenport=6624, mac='00:00:00:00:00:24')
    spSw = net.addSwitch('sw25', listenport=6625, mac='00:00:00:00:00:25')
    seSw = net.addSwitch('sw26', listenport=6626, mac='00:00:00:00:00:26')
    toSw = net.addSwitch('sw27', listenport=6627, mac='00:00:00:00:00:27')
    pbcSw = net.addSwitch('sw28', listenport=6628, mac='00:00:00:00:00:28')
    miaSw = net.addSwitch('sw29', listenport=6629, mac='00:00:00:00:00:29')
        
    # Add links
    net.addLink(acSw, roSw, port1=1, port2=1)
    net.addLink(roSw, mtSw, port1=2, port2=1)
    net.addLink(mtSw, msSw, port1=2, port2=1)
    net.addLink(mtSw, goSw, port1=3, port2=1)
    net.addLink(msSw, prSw, port1=2, port2=1)
    net.addLink(prSw, rsSw, port1=2, port2=1)
    net.addLink(prSw, spSw, port1=3, port2=1)
    net.addLink(prSw, scSw, port1=4, port2=1)
    net.addLink(scSw, spSw, port1=2, port2=2)
    net.addLink(spSw, rjSw, port1=3, port2=1)
    net.addLink(rjSw, esSw, port1=2, port2=1)
    net.addLink(rjSw, dfSw, port1=3, port2=1)
    net.addLink(goSw, toSw, port1=2, port2=1)
    net.addLink(goSw, dfSw, port1=3, port2=2)
    net.addLink(toSw, paSw, port1=2, port2=1)
    net.addLink(dfSw, amSw, port1=3, port2=1)
    net.addLink(dfSw, mgSw, port1=4, port2=1)
    net.addLink(esSw, baSw, port1=2, port2=1)
    net.addLink(baSw, peSw, port1=2, port2=1)
    net.addLink(baSw, seSw, port1=3, port2=1)
    net.addLink(baSw, mgSw, port1=4, port2=2)
    net.addLink(mgSw, ceSw, port1=3, port2=1)
    net.addLink(seSw, alSw, port1=2, port2=2)
    net.addLink(alSw, peSw, port1=1, port2=2)
    net.addLink(amSw, paSw, port1=2, port2=2)
    net.addLink(amSw, rrSw, port1=3, port2=1)
    net.addLink(rrSw, ceSw, port1=2, port2=2)
    net.addLink(spSw, mgSw, port1=4, port2=4)
    net.addLink(spSw, ceSw, port1=5, port2=3)
    net.addLink(ceSw, maSw, port1=4, port2=1)
    net.addLink(ceSw, rnSw, port1=5, port2=1)
    net.addLink(ceSw, peSw, port1=6, port2=3)
    net.addLink(maSw, paSw, port1=2, port2=3)
    net.addLink(paSw, apSw, port1=4, port2=1)
    net.addLink(paSw, piSw, port1=5, port2=1)
    net.addLink(piSw, peSw, port1=2, port2=4)
    net.addLink(rnSw, pbjSw, port1=2, port2=1)
    net.addLink(pbjSw, pbcSw, port1=2, port2=1)
    net.addLink(pbcSw, peSw, port1=2, port2=5)
    net.addLink(spSw, miaSw, port1=6, port2=1)
    net.addLink(ceSw, miaSw, port1=7, port2=2)
    net.addLink(rsSw, scSw, port1=2, port2=3)

    # Add hosts
    rsHost = net.addHost('h1', mac='00:00:00:00:01:00', cls=VLANHost, vlan=1)
    miaHost = net.addHost('h2', mac='00:00:00:00:02:00', cls=VLANHost, vlan=2)
    baHost = net.addHost('h3', mac='00:00:00:00:03:00', cls=VLANHost, vlan=3)
    acHost = net.addHost('h4', mac='00:00:00:00:04:00', cls=VLANHost, vlan=4)
    
    # Add links to hosts
    net.addLink(rsHost, rsSw, port1=1, port2=3)
    net.addLink(miaHost, miaSw, port1=1, port2=3)
    net.addLink(baHost, baSw, port1=1, port2=5)
    net.addLink(acHost, acSw, port1=1, port2=3)
    
    # Add controllers:
    acCtlr = net.addController('ctlr1', controller=RemoteController, ip='127.0.0.1', port=6601)
    alCtlr = net.addController('ctlr2', controller=RemoteController, ip='127.0.0.1', port=6602)
    apCtlr = net.addController('ctlr3', controller=RemoteController, ip='127.0.0.1', port=6603)
    amCtlr = net.addController('ctlr4', controller=RemoteController, ip='127.0.0.1', port=6604)
    baCtlr = net.addController('ctlr5', controller=RemoteController, ip='127.0.0.1', port=6605)
    ceCtlr = net.addController('ctlr6', controller=RemoteController, ip='127.0.0.1', port=6606)
    dfCtlr = net.addController('ctlr7', controller=RemoteController, ip='127.0.0.1', port=6607)
    esCtlr = net.addController('ctlr8', controller=RemoteController, ip='127.0.0.1', port=6608)
    goCtlr = net.addController('ctlr9', controller=RemoteController, ip='127.0.0.1', port=6609)
    maCtlr = net.addController('ctlr10', controller=RemoteController, ip='127.0.0.1', port=6610)
    mtCtlr = net.addController('ctlr11', controller=RemoteController, ip='127.0.0.1', port=6611)
    msCtlr = net.addController('ctlr12', controller=RemoteController, ip='127.0.0.1', port=6612)
    mgCtlr = net.addController('ctlr13', controller=RemoteController, ip='127.0.0.1', port=6613)
    paCtlr = net.addController('ctlr14', controller=RemoteController, ip='127.0.0.1', port=6614)
    pbjCtlr = net.addController('ctlr15', controller=RemoteController, ip='127.0.0.1', port=6615)
    prCtlr = net.addController('ctlr16', controller=RemoteController, ip='127.0.0.1', port=6616)
    peCtlr = net.addController('ctlr17', controller=RemoteController, ip='127.0.0.1', port=6617)
    piCtlr = net.addController('ctlr18', controller=RemoteController, ip='127.0.0.1', port=6618)
    rjCtlr = net.addController('ctlr19', controller=RemoteController, ip='127.0.0.1', port=6619)
    rnCtlr = net.addController('ctlr20', controller=RemoteController, ip='127.0.0.1', port=6620)
    rsCtlr = net.addController('ctlr21', controller=RemoteController, ip='127.0.0.1', port=6621)
    roCtlr = net.addController('ctlr22', controller=RemoteController, ip='127.0.0.1', port=6622)
    rrCtlr = net.addController('ctlr23', controller=RemoteController, ip='127.0.0.1', port=6623)
    scCtlr = net.addController('ctlr24', controller=RemoteController, ip='127.0.0.1', port=6624)
    spCtlr = net.addController('ctlr25', controller=RemoteController, ip='127.0.0.1', port=6625)
    seCtlr = net.addController('ctlr26', controller=RemoteController, ip='127.0.0.1', port=6626)
    toCtlr = net.addController('ctlr27', controller=RemoteController, ip='127.0.0.1', port=6627)
    pbcCtlr = net.addController('ctlr28', controller=RemoteController, ip='127.0.0.1', port=6628)
    miaCtlr = net.addController('ctlr29', controller=RemoteController, ip='127.0.0.1', port=6629)


    # Start it up
    net.build()
    print "net.build"

    # Start all the switches
    acSw.start([acCtlr])
    alSw.start([alCtlr])
    apSw.start([apCtlr])
    amSw.start([amCtlr])
    baSw.start([baCtlr])
    ceSw.start([ceCtlr])
    dfSw.start([dfCtlr])
    esSw.start([esCtlr])
    goSw.start([goCtlr])
    maSw.start([maCtlr])
    mtSw.start([mtCtlr])
    msSw.start([msCtlr])
    mgSw.start([mgCtlr])
    paSw.start([paCtlr])
    pbjSw.start([pbjCtlr])
    prSw.start([prCtlr])
    peSw.start([peCtlr])
    piSw.start([piCtlr])
    rjSw.start([rjCtlr])
    rnSw.start([rnCtlr])
    rsSw.start([rsCtlr])
    roSw.start([roCtlr])
    rrSw.start([rrCtlr])
    scSw.start([scCtlr])
    spSw.start([spCtlr])
    seSw.start([seCtlr])
    toSw.start([toCtlr])
    pbcSw.start([pbcCtlr])
    miaSw.start([miaCtlr])
    net.start()
    print "net.start"
    CLI(net)
    print "CLI(net)"
    net.stop()
    print "net.stop"

if __name__ == '__main__':
    MyTopo()
