FROM metabrainz/docker-anon-ftp

RUN apt-get update && apt-get install -y ftp

COPY server.py /root/

CMD python3 /root/server.py