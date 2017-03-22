FROM ubuntu:16.04

RUN apt update && apt install -y git python-virtualenv pypy python-pip

# This really should point to a particular version
RUN git clone https://github.com/atlanticwave-sdx/atlanticwave-proto.git

# Virtualenv setup
RUN virtualenv -p /usr/bin/pypy /appenv
RUN . /appenv/bin/activate
RUN pip install -r atlanticwave-proto/requirements.txt
#run pip install dataset

# Install and patch Ryu - there's a small bug with Ryu that needs to be patched
RUN pip install ryu
RUN ./atlanticwave-proto/vendor-updates/update-ryu-flags.sh `pip show ryu | grep Location: | awk '{print $NF}'`

# Setup the PYTHONPATH script
ENV PYTHONPATH $PYTHONPATH:/atlanticwave-proto

COPY run_lc.sh .

CMD /bin/bash run_lc.sh; /bin/bash
#CMD /bin/bash
