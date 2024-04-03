# syntax=docker/dockerfile:1.3

FROM python:3.7-slim-buster

RUN echo "[global] \n extra-index-url=https://www.piwheels.org/simple" >> /etc/pip.conf

#COPY deployment/testbed/mosaikrtu/ replay_csv/deployment/testbed/mosaikrtu/
#COPY deployment/testbed/ replay_csv/deployment/testbed/

#COPY deployment/testbed/data/config_files/ replay_csv/deployment/testbed/data/config_files/
COPY replay_csv/ replay_csv/

# Install dependencies
COPY replay_csv/requirements.txt replay_csv/requirements.txt
RUN pip install -r replay_csv/requirements.txt

EXPOSE 10502 10503
ENTRYPOINT [ "python", "-u", "replay_csv/replay.py"]