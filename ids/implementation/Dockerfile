# syntax=docker/dockerfile:1.3

FROM python:3.7-slim-buster
WORKDIR /ids

RUN echo "[global] \n extra-index-url=https://www.piwheels.org/simple" >> /etc/pip.conf

RUN apt-get update
RUN apt-get -y install libffi-dev

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install -Iv cryptography==37.0.4

COPY implementation/requirements.txt implementation/requirements.txt
RUN pip install -r implementation/requirements.txt

COPY . .