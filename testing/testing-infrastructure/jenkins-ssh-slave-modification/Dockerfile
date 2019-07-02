FROM jenkins/ssh-slave
MAINTAINER Sean Donovan <sdonovan@gatech.edu>

USER root
RUN apt-get update && apt-get -y install python-pip
RUN pip install virtualenv

# Mininet-specific commands
# Based on https://github.com/iwaseyusuke/docker-mininet/blob/master/Dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    iproute2 \
    iputils-ping \
    mininet \
    net-tools \
    openvswitch-switch \
    openvswitch-testcontroller \
    tcpdump \
    vim \
    x11-xserver-utils \
    xterm

RUN service openvswitch-switch start

EXPOSE 6633 6653 6640
# End MININET

ENTRYPOINT ["setup-sshd"]
