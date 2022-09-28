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
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && \
    apt-get update -y && \
    apt-get install google-cloud-cli -y

COPY . /app/