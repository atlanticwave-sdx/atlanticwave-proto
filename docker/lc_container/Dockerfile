FROM ubuntu:18.04

RUN apt update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:pypy/ppa
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev pypy3 python3-venv git net-tools vim

RUN update-alternatives --remove python /usr/bin/python2
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 10

# Virtualenv setup
#RUN virtualenv -p /usr/bin/pypy /appenv
#RUN . /appenv/bin/activate
#RUN pip install -r atlanticwave-proto/requirements.txt
#run pip install dataset

# This really should point to a particular version
RUN git clone -b python3upgrade https://github.com/atlanticwave-sdx/atlanticwave-proto.git

RUN python -m venv appenv
RUN . appenv/bin/activate

RUN pip3 install future
RUN pip3 install -r atlanticwave-proto/requirements.txt

# Install and patch Ryu - there's a small bug with Ryu that needs to be patched
#RUN pip3 install ryu
RUN ./atlanticwave-proto/vendor-updates/update-ryu-flags.sh `pip3 show ryu | grep Location: | awk '{print $NF}'`

# Setup the PYTHONPATH script
ENV PYTHONPATH /atlanticwave-proto:$PYTHONPATH

COPY run_lc.sh .
COPY ./*.manifest ./

CMD /bin/bash run_lc.sh; /bin/bash
#CMD /bin/bash
