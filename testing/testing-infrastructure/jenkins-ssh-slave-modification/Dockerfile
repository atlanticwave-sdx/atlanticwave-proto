FROM jenkins/ssh-slave
MAINTAINER Sean Donovan <sdonovan@gatech.edu>

USER root
RUN apt-get update && apt-get -y install python-pip
RUN pip install virtualenv

ENTRYPOINT ["setup-sshd"]
