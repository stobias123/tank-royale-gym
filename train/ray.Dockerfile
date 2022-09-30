FROM rayproject/ray:2.0.0-py38-cpu
USER root
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 build-essential -y
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
