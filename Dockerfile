FROM python:3.9-slim-bullseye
RUN apt-get update
RUN apt-get -y install gcc libcurl4-openssl-dev libssl-dev

ADD credentials /credentials
ADD data /data

WORKDIR /pipeline
ADD pipeline .
RUN pip install .
