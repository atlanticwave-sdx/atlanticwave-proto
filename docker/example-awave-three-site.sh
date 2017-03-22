#!/bin/bash
# This is an example of how to run a three site version of containerized
# AtlanticWave/SDX controllers. The SDXIP should likely point to the public
# IP address of the server running the SDX controller container, rather 
# than pointing to localhost.

docker rm threesitesdxctlr
docker rm threesitelcatl
docker rm threesitelcmia
docker rm threesitelcgru


docker run -e MANIFEST="../demo/corsa-three-site.manifest" -e IPADDR="0.0.0.0" -e PORT="5000" -e LCPORT="5555" -p 5000:5000 -p 5555:5555 -idt --name=threesitesdxctlr sdx_container
docker run -e MANIFEST="../demo/corsa-three-site.manifest" -e SITE="atl" -e SDXIP="127.0.0.1" -p 6633:6633 -idt --name=threesitelcatl lc_container
docker run -e MANIFEST="../demo/corsa-three-site.manifest" -e SITE="mia" -e SDXIP="127.0.0.1" -p 6643:6643 -idt --name=threesitelcmia lc_container
docker run -e MANIFEST="../demo/corsa-three-site.manifest" -e SITE="gru" -e SDXIP="127.0.0.1" -p 6653:6653 -idt --name=threesitelcgru lc_container


docker ps
