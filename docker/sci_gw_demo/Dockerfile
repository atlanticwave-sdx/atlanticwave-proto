FROM ubuntu:18.04

RUN apt update && apt install -y iputils-ping iperf net-tools
RUN apt install -y python3 curl

COPY science_gateway.py /root/

CMD python3 /root/science_gateway.py