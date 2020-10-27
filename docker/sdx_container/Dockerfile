FROM ubuntu:18.04

ARG GITHUB_BRANCH=develop

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

COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY ./*.manifest ./

# This really should point to a particular version
RUN git clone -b ${GITHUB_BRANCH} https://github.com/atlanticwave-sdx/atlanticwave-proto.git
RUN cat atlanticwave-proto/requirements.txt
RUN pip3 install -r atlanticwave-proto/requirements.txt

ENTRYPOINT ["/docker-entrypoint.sh"]
