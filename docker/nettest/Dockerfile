FROM ubuntu:16.04

RUN apt update && apt install -y iputils-ping iperf net-tools

COPY awhosts /root/

CMD cat /root/awhosts >> /etc/hosts; /bin/bash

