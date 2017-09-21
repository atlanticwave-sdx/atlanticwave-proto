#!/bin/bash

sysctl net.ipv4.conf.all.rp_filter=0

modprobe 8021q
ifconfig p1p3 up
ifconfig p1p4 up

vconfig add p1p3 100
ifconfig p1p3.100 up

vconfig add p1p3 200
ifconfig p1p3.200 up


cd ~/pipework
./pipework p1p3.100 $(docker run -idt --name=vlan100 nettest) 10.10.10.100/24
./pipework p1p3.200 $(docker run -idt --name=vlan200 nettest) 10.10.10.200/24



