# AtlanticWave-SDX Production Testbed Setup 

## Testbed Topology

![alt text](figures/AW-SDX-Production_Setup-0-Topology.png)
Note: Santiago/Chile is shown tentatively. Actual connection path may be different.

## Node Layout

![alt text](figures/AW-SDX-Production_Setup-2-Node_Layout.png)

## Tunnel Layout

![alt text](figures/AW-SDX-Production_Setup-3-Tunnel_Layout-L2Multipoint.png)


```
# Out-of-band management

- Miami
- miami-corsa     : 67.17.206.198
- miami-vm        : 190.103.186.106

- Atlanta
- sox-corsa       : 143.215.216.3
- Baremetal server: 128.61.149.224
- awsdx-ctrl (VM) : 128.61.149.223
- awsdx-app (VM)  : 128.61.149.224

# OpenFlow Conrol Connection

# SDX Controller
128.61.149.224 awsdx-app sdx.atlanticwave-sdx.net

# Local Controllers 
128.61.149.223  awsdx-ctrl  lc-atl.atlanticwave-sdx.net
190.103.186.106 miami-vm    lc-mia.atlanticwave-sdx.net
190.103.186.107 santiago-vm lc-chl.atlanticwave-sdx.net

# Corsa Switches
143.215.216.3 sox-corsa      corsa-atl.atlanticwave-sdx.net
67.17.206.198 miami-corsa    corsa-mia.atlanticwave-sdx.net
67.17.206.199 santiago-corsa corsa-chl.atlanticwave-sdx.net

```

```
# In-band management
# VLAN 1805 for MIAMI and VLAN 3621 for ATLANTA is used for in-band management

# SDX Controller
10.14.11.254 sdx.atlanticwave-sdx.net

# Local Controllers
10.14.11.1    lc-atl.atlanticwave-sdx.net
10.14.11.2    lc-mia.atlanticwave-sdx.net
10.14.11.3    lc-chl.atlanticwave-sdx.net

```

## Corsa Switches

Configuration on the switches prior to the deployment is saved on the files.
- [sox-corsa](config/sox-corsa.cfg)
- [miami-corsa](config/miami-corsa.cfg)

Also, backup of the active-configuration is saved on the switches.

```
corsa-sdx-56m# show file backup full 
.
├── [3.8K Jun  1  3:00:02]  corsa-sdx-56m.bkp.0.030002.12.2020.06.01.030002.tar.bz2
├── [3.8K Jun  8  3:00:02]  corsa-sdx-56m.bkp.0.030002.12.2020.06.08.030001.tar.bz2
├── [5.1K Jun  9 18:08:06]  corsa-sdx-56m.bkp.0.030002.12.2020.06.09.180806.tar.bz2
├── [3.8K Jun 15  3:00:01]  corsa-sdx-56m.bkp.0.030002.12.2020.06.15.030001.tar.bz2
├── [3.8K Jun 22  3:00:02]  corsa-sdx-56m.bkp.0.030002.12.2020.06.22.030002.tar.bz2
└── [3.4K Jun 25  2:58:11]  corsa-atl.atlanticwave-sdx.net.p12
```


Ports are set to `passthrough` mode. (ctag mode strips off the VLAN tag that prevent flows with `dl_vlan` match field being pushed properly. This can be a pure openflow behavior that needs to be elaborated.)

Openflow control connection is established through default namespace (and associated out-of-band management interface).


### Set port tunnel-modes


```
#
# sox-corsa
#

```

```
#
# miami-corsa
#

# Primary forwarding ports
amlight-corsa# configure port 1 tunnel-mode passthrough 
amlight-corsa# configure port 2 tunnel-mode passthrough
amlight-corsa# configure port 3 tunnel-mode passthrough
amlight-corsa# configure port 4 tunnel-mode passthrough
amlight-corsa# configure port 10 tunnel-mode passthrough

# Rate-limiting ports 
amlight-corsa# configure port 23 tunnel-mode passthrough 
amlight-corsa# configure port 24 tunnel-mode passthrough
amlight-corsa# configure port 25 tunnel-mode ctag
amlight-corsa# configure port 26 tunnel-mode ctag

# Multipoint Rate-limiting ports
amlight-corsa# configure port 13 tunnel-mode ctag
amlight-corsa# configure port 14 tunnel-mode ctag
amlight-corsa# configure port 15 tunnel-mode ctag
amlight-corsa# configure port 16 tunnel-mode ctag
```




### Create VFCs 

```
#
# sox-corsa
#


```

```
#
# miami-corsa
#

# Create Primary VFC

amlight-corsa# configure bridge add br22 openflow resources 10
amlight-corsa# configure bridge br22 dpid 0xCA
amlight-corsa# configure bridge br22 tunnel attach ofport 1 port 1
amlight-corsa# configure bridge br22 tunnel attach ofport 2 port 2
amlight-corsa# configure bridge br22 tunnel attach ofport 3 port 3
amlight-corsa# configure bridge br22 tunnel attach ofport 4 port 4
amlight-corsa# configure bridge br22 tunnel attach ofport 10 port 10
amlight-corsa# configure bridge br22 tunnel attach ofport 23 port 23
amlight-corsa# configure bridge br22 tunnel attach ofport 24 port 24
amlight-corsa# configure bridge br22 controller add CONTbr22 190.103.186.106 6682


# Create Multipoint Rate-limiting VFC

amlight-corsa# configure bridge add br19 openflow resources 10
amlight-corsa# configure bridge br19 controller add CONTbr19 172.17.1.1 6653 

# Create L2Tunnel Rate-limiting VFC


```


### Rate Limiting VFC

Physical ports are in ctag tunnel-mode.
On RENCI-1, DUKE, UNC, NCSU switches Port 21 and 22 are attached to the rate-limiting VFC.
On RENCI-2 switch ports 27 and 28 are attached to the rate-limiting VFC.

```
# Create rate limiting VFC (br20) on RENCI-1 | RENCI-2 | DUKE | UNC | NCSU
configure bridge add br20 vpws resources 2
configure bridge br20 controller add Eline 172.17.2.1 6653
application eline configure connection add atlanticwave 21 22 "Rate Limiting VFC"
```

Scripts in ratelimiting-vfc can be used to delete and create the rate-limiting VFCs.

```
python make-rate-limiting-switch-clean-renci.py 
python make-rate-limiting-switch-clean-duke.py 
python make-rate-limiting-switch-clean-unc.py 
python make-rate-limiting-switch-clean-ncsu.py 
python make-rate-limiting-switch-clean-renci-2.py

or 

re-create-all.sh

```


## Run SDX Controller and Local Controllers

Script `aw.sh` can be used to build docker images and run the containers for sdx and local controllers.
Type of the controller and site names are extracted from hostnames. 

```
# Build docker images
/root/aw.sh -R <REPO> -B <BRANCH> -b
Default Repo: https://github.com/RENCI-NRIG/atlanticwave-proto.git
Default Branch: master-rci

/root/aw.sh -B renci-corsa-ben -b

# Run docker containers (in detached mode)
/root/aw.sh -m detached -r 

# Run docker containers (interactive)
/root/aw.sh -r 
```

