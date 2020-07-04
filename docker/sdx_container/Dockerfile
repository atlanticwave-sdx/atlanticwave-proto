FROM ubuntu:16.04

RUN apt update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:pypy/ppa
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev pypy3 python3-venv git net-tools vim

RUN update-alternatives --remove python /usr/bin/python2
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 10

# Virtualenv setup
#RUN virtualenv -p /usr/bin/pypy /appenv
#RUN . /appenv/bin/activate
#run pip install dataset

RUN python -m venv appenv
RUN . appenv/bin/activate

RUN pip3 install future
# Setup the PYTHONPATH script
ENV PYTHONPATH /atlanticwave-proto:$PYTHONPATH

COPY run_sdx.sh .
COPY ./*.manifest ./

# This really should point to a particular version
RUN git clone -b python3upgrade https://github.com/atlanticwave-sdx/atlanticwave-proto.git
RUN cat atlanticwave-proto/requirements.txt
RUN pip3 install -r atlanticwave-proto/requirements.txt

CMD /bin/bash run_sdx.sh; /bin/bash
#CMD /bin/bash
