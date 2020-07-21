FROM ubuntu:16.04

RUN apt update && apt install -y git python-virtualenv pypy python-pip net-tools vim

# This really should point to a particular version
RUN git clone -b master https://github.com/atlanticwave-sdx/atlanticwave-proto.git

# Virtualenv setup
RUN virtualenv -p /usr/bin/pypy /appenv
RUN . /appenv/bin/activate

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r atlanticwave-proto/requirements.txt
RUN pip install pip==9.0.3

# Setup the PYTHONPATH script
ENV PYTHONPATH $PYTHONPATH:/atlanticwave-proto

COPY run_sdx.sh .
COPY ./*.manifest ./

CMD /bin/bash run_sdx.sh; /bin/bash
#CMD /bin/bash
