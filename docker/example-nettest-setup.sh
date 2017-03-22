#!/bin/bash

sysctl net.ipv4.conf.all.rp_filter=0

modprobe 8021q
ifconfig p1p1 up
ifconfig p1p2 up
ifconfig p1p3 up

vconfig add p1p1 11
ifconfig p1p1.11 up

vconfig add p1p1 12
ifconfig p1p1.12 up

vconfig add p1p1 13
ifconfig p1p1.13 up


vconfig add p1p2 21
ifconfig p1p2.21 up

vconfig add p1p2 22
ifconfig p1p2.22 up

vconfig add p1p2 23
ifconfig p1p2.23 up


vconfig add p1p3 31
ifconfig p1p3.31 up

vconfig add p1p3 32
ifconfig p1p3.32 up

vconfig add p1p3 33
ifconfig p1p3.33 up


cd pipework
./pipework p1p1.11 $(docker run -idt --name=vlan11 nettest) 10.10.10.11/24
./pipework p1p1.12 $(docker run -idt --name=vlan12 nettest) 10.10.10.12/24
./pipework p1p1.13 $(docker run -idt --name=vlan13 nettest) 10.10.10.13/24

./pipework p1p2.21 $(docker run -idt --name=vlan21 nettest) 10.10.10.21/24
./pipework p1p2.22 $(docker run -idt --name=vlan22 nettest) 10.10.10.22/24
./pipework p1p2.23 $(docker run -idt --name=vlan23 nettest) 10.10.10.23/24

./pipework p1p3.31 $(docker run -idt --name=vlan31 nettest) 10.10.10.31/24
./pipework p1p3.32 $(docker run -idt --name=vlan32 nettest) 10.10.10.32/24
./pipework p1p3.33 $(docker run -idt --name=vlan33 nettest) 10.10.10.33/24
cd ..
