FROM ubuntu:16.04

RUN apt update && apt install -y git python-virtualenv pypy python-pip net-tools

RUN git clone https://github.com/atlanticwave-sdx/atlanticwave-proto.git

RUN pip install ryu

ENV PYTHONPATH $PYTHONPATH:.:/atlanticwave-proto/testing/util

CMD /bin/bash