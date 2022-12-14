FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 python3.9 python3-pip git
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

RUN ln -s /usr/bin/python3 /usr/bin/python
#RUN pip3 install git+https://github.com/stobias123/tank-royale-gym
RUN pip install git+https://github.com/stobias123/tank_royal_manager

RUN pip3 install --upgrade mlflow boto3 pydantic kubernetes stable-baselines3 pydantic opencv-python torchvision pytorch_lightning
WORKDIR /app
COPY setup.py setup.py
COPY tank_royal_gym tank_royal_gym
WORKDIR /app
RUN pip3 install --force-reinstall .
COPY train/sb3.py sb3.py
COPY train/wrappers.py wrappers.py
ENTRYPOINT ["python"]
CMD ["/app/sb3.py"]