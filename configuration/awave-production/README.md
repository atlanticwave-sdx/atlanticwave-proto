# AtlanticWave-SDX Production Testbed Setup 

## Testbed Topology

![alt text](figures/AW-SDX-Production_Setup-0-Topology.png)
Note: Santiago/Chile is shown tentatively. Actual connection path may be different.

## Node Layout

![alt text](figures/AW-SDX-Production_Setup-2-Node_Layout.png)

## Tunnel Layout

![alt text](figures/AW-SDX-Production_Setup-2-Node_Layout.png)


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

Ports are set to `passthrough` mode. (ctag mode strips off the VLAN tag that prevent flows with `dl_vlan` match field being pushed properly. This can be a pure openflow behavior that needs to be elaborated.)

Openflow control connection is established through default namespace (and associated out-of-band management interface).


### Set port tunnel-modes

```
# RENCI-1
configure port 1 tunnel-mode passthrough
configure port 2 tunnel-mode passthrough
configure port 11 tunnel-mode passthrough
configure port 12 tunnel-mode passthrough
configure port 23 tunnel-mode passthrough
configure port 30 tunnel-mode passthrough
configure port 19 tunnel-mode passthrough
configure port 20 tunnel-mode passthrough

```


### Create VFCs on all Corsa switches

```
# RENCI-1

configure bridge add br21 openflow resources 10
configure bridge br21 dpid 0xC9
configure bridge br21 tunnel attach ofport 1 port 1
configure bridge br21 tunnel attach ofport 2 port 2
configure bridge br21 tunnel attach ofport 11 port 11
configure bridge br21 tunnel attach ofport 12 port 12
configure bridge br21 tunnel attach ofport 23 port 23
configure bridge br21 tunnel attach ofport 30 port 30
configure bridge br21 tunnel attach ofport 19 port 19 
configure bridge br21 tunnel attach ofport 20 port 20 
configure bridge br21 controller add CONTbr21 192.168.201.196 6681

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

