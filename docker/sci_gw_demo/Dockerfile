FROM ubuntu:18.04

RUN apt update && apt install -y iputils-ping iperf net-tools

COPY science_gateway.py /root/

CMD python3 /root/science_gateway.py