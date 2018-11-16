# RENCI Testbed Setup

## Node Layout

![alt text](figures/AW-SDX-Node-Layout.png)

Direct Link: https://drive.google.com/file/d/1BHdOv4X62mmVrFEbLGE5By1Nt3GNLBEo/view?usp=sharing

```
# Out-of-band management

# SDX Controller
192.168.201.156 atlanticwave-sdx-controller.renci.ben

# Local Controllers
192.168.201.171   atlanticwave-lc-renci.renci.ben
192.168.202.172   atlanticwave-lc-duke.renci.ben
192.168.203.173   atlanticwave-lc-unc.renci.ben
192.168.204.174   atlanticwave-lc-ncsu.renci.ben

# Corsa Switches
192.168.201.168   corsa-2.renci.ben
192.168.202.30    corsa-1.duke.ben
192.168.203.30    corsa-1.unc.ben
192.168.204.30    corsa-1.ncsu.ben

```

```
# In-band management
# VLAN 1411 is used for in-band management

# SDX Controller
10.14.11.254 atlanticwave-sdx-controller.renci.ben

# Local Controllers
10.14.11.101    atlanticwave-lc-renci.renci.ben
10.14.11.102    atlanticwave-lc-duke.renci.ben
10.14.11.103    atlanticwave-lc-unc.renci.ben
10.14.11.104    atlanticwave-lc-ncsu.renci.ben

# Corsa Switches
10.14.11.201    corsa-2.renci.ben
10.14.11.202    corsa-1.duke.ben
10.14.11.203    corsa-1.unc.ben
10.14.11.204    corsa-1.ncsu.ben

```





## Corsa Switches

Guest namespaces are created and management tunnels are attached to provde access for in-band management of the overlay VFCs. 
(Ref: DP2000_Config_Guide_UG-CDD0028-000-Rev002.pdf , Section 4 Management Interfaces, Page 27)
Management tunnels are primarily attached for management ports (Port 1 and 2 on each switch). 
If the local controller is running on the bf40g node, then a management tunnel needs to be attached for the node as well. 

![alt text](figures/AW-SDX-Corsa-Tunnel-Layout.png)

Direct Link: https://drive.google.com/file/d/1BHdOv4X62mmVrFEbLGE5By1Nt3GNLBEo/view?usp=sharing

```
### Configure Guest Namespaces on Corsa Switches

# RENCI
configure netns add of-mgt-1411
configure netns of-mgt-1411 mode static 10.14.11.201 255.255.255.0 10.14.11.254
configure netns of-mgt-1411 tunnel attach 1 mgt-id mgt1 vlan-id 1411 shaped-rate 1000
configure netns of-mgt-1411 tunnel attach 2 mgt-id mgt2 vlan-id 1411 shaped-rate 1000
configure netns of-mgt-1411 tunnel attach 31 mgt-id mgt3 vlan-id 1411 shaped-rate 1000
configure netns of-mgt-1411 tunnel attach 10 mgt-id mgt4 vlan-id 1411 shaped-rate 1000

# DUKE
configure netns add of-mgt-1411
configure netns of-mgt-1411 mode static 10.14.11.202 255.255.255.0 10.14.11.254
configure netns of-mgt-1411 tunnel attach 1 mgt-id mgt1 vlan-id 1411 shaped-rate 1000
configure netns of-mgt-1411 tunnel attach 2 mgt-id mgt2 vlan-id 1411 shaped-rate 1000
configure netns of-mgt-1411 tunnel attach 11 mgt-id mgt3 vlan-id 1411 shaped-rate 1000

# UNC
configure netns add of-mgt-1411
configure netns of-mgt-1411 mode static 10.14.11.203 255.255.255.0 10.14.11.254
configure netns of-mgt-1411 tunnel attach 1 mgt-id mgt1 vlan-id 1411 shaped-rate 1000
configure netns of-mgt-1411 tunnel attach 11 mgt-id mgt2 vlan-id 1411 shaped-rate 1000

# NCSU
configure netns add of-mgt-1411
configure netns of-mgt-1411 mode static 10.14.11.204 255.255.255.0 10.14.11.254
configure netns of-mgt-1411 tunnel attach 2 mgt-id mgt1 vlan-id 1411 shaped-rate 1000
configure netns of-mgt-1411 tunnel attach 10 mgt-id mgt2 vlan-id 1411 shaped-rate 1000

```

Create VFCs on all Corsa switches

```
# Create bandwidth limiter VFC (br20) on all switches
configure bridge add br20 vpws resources 2
configure bridge br20 controller add Eline 172.17.2.1 6653

# Create VFC on renci switch (DPID 7573453565774) 
configure bridge add br21 openflow resources 10 netns of-mgt-1411 
configure bridge br21 controller add CONTbr21 10.14.11.101 6681
configure bridge br21 tunnel attach ofport 1 port 1 vlan-range 1416-1499
configure bridge br21 tunnel attach ofport 2 port 2 vlan-range 1416-1499
configure bridge br21 tunnel attach ofport 19 port 19 vlan-range 1416-1499
configure bridge br21 tunnel attach ofport 20 port 20 vlan-range 1416-1499

# Create VFC on duke switch (DPID 279552153404237)
configure bridge add br22 openflow resources 10 netns of-mgt-1411
configure bridge br22 controller add CONTbr22 10.14.11.102 6682
configure bridge br22 tunnel attach ofport 1 port 1 vlan-range 1416-1499
configure bridge br22 tunnel attach ofport 2 port 2 vlan-range 1416-1499
configure bridge br22 tunnel attach ofport 19 port 19 vlan-range 1416-1499
configure bridge br22 tunnel attach ofport 20 port 20 vlan-range 1416-1499

# Create VFC on unc switch (DPID 236202656471118)
configure bridge add br23 openflow resources 10 netns of-mgt-1411 
configure bridge br23 controller add CONTbr23 10.14.11.103 6683
configure bridge br23 tunnel attach ofport 1 port 1 vlan-range 1416-1499
configure bridge br23 tunnel attach ofport 2 port 2 vlan-range 1416-1499
configure bridge br23 tunnel attach ofport 19 port 19 vlan-range 1416-1499
configure bridge br23 tunnel attach ofport 20 port 20 vlan-range 1416-1499

# Create VFC on ncsu switch (DPID 209215245675848)
configure bridge add br24 openflow resources 10 netns of-mgt-1411 
configure bridge br24 controller add CONTbr24 10.14.11.104 6684
configure bridge br24 tunnel attach ofport 1 port 1 vlan-range 1416-1499
configure bridge br24 tunnel attach ofport 2 port 2 vlan-range 1416-1499
configure bridge br24 tunnel attach ofport 19 port 19 vlan-range 1416-1499
configure bridge br24 tunnel attach ofport 20 port 20 vlan-range 1416-1499

```

## Run Controllers

Script `aw.sh` can be used to build docker images and run the containers for sdx and local controllers.
Type of the controller and site names are extracted from hostnames. 

```
# Build docker images
/root/aw.sh -b

# Run docker containers
/root/aw.sh -r 

```





 
