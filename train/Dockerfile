FROM nvidia/cuda:11.7.0-devel-ubuntu20.04

# you'll want git for sure my dude
RUN apt-get update && \
  apt-get install -y \
  git \
  sqlite3 \
  python3 \
  python3-pip \
  unzip \
  curl

COPY ./requirements.txt /src/requirements.txt
RUN cd /src/ && pip install -r requirements.txt

RUN ln -s /usr/bin/python3 /usr/bin/python

COPY . /app/