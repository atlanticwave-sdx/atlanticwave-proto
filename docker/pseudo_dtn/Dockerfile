FROM metabrainz/docker-anon-ftp

RUN apt-get update && apt-get install -y ftp
RUN apt-get install -y python3-pip

RUN pip3 install flask flask_restful

COPY server.py /root/

CMD python3 /root/server.py