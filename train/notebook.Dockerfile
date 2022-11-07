FROM public.ecr.aws/j1r0q0g6/notebooks/notebook-servers/jupyter-pytorch-full:v1.5.0
USER root
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 build-essential -y
RUN apt-get remove -y python3.8 && apt-get install -y python3.7
USER jovyan
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
