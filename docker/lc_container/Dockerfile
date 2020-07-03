FROM ubuntu:16.04

RUN update-alternatives --remove python /usr/bin/python2
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 10
RUN add-apt-repository ppa:pypy/ppa
RUN apt update && apt install -y git python-virtualenv pypy python-pip net-tools vim pypy3 python3-pip python3-venv

# This really should point to a particular version
RUN git clone -b python3upgrade https://github.com/atlanticwave-sdx/atlanticwave-proto.git

# Virtualenv setup
#RUN virtualenv -p /usr/bin/pypy /appenv
#RUN . /appenv/bin/activate
#RUN pip install -r atlanticwave-proto/requirements.txt
#run pip install dataset

RUN python -m venv appenv
RUN source app-env/bin/activate

# Install and patch Ryu - there's a small bug with Ryu that needs to be patched
RUN pip3 install ryu
RUN ./atlanticwave-proto/vendor-updates/update-ryu-flags.sh `pip show ryu | grep Location: | awk '{print $NF}'`

# Setup the PYTHONPATH script
ENV PYTHONPATH $PYTHONPATH:.:/atlanticwave-proto

COPY run_lc.sh .
COPY ./*.manifest ./

CMD /bin/bash run_lc.sh; /bin/bash
#CMD /bin/bash
