from concurrent import futures
import time
import logging
import subprocess
import gym
from gym import spaces
import logging
import time
import numpy
import json
import http.client
import io, base64
from PIL import Image
from base import BaseRobocodeEnv


class KubernetesEnv(BaseRobocodeEnv):
    metadata = {'render.modes': ['rgb_array']}

    def __init__(self):
        self.__version__ = "0.1.0"
        super(BaseRobocodeEnv, self).__init__()
        #logging.info(f"[BaseRobocodeEnv Env] - Version {self.__version__}")
        # Env Setup - WASD to integer.
        self.HEIGHT=600
        self.WIDTH=800
        self.action_space = spaces.Discrete(16)
        self.observation_space = spaces.Box(low=0, high=255,
                                        shape=(self.HEIGHT, self.WIDTH, 3), dtype=numpy.uint8)

    def reset(self):
      pass

    def step(self, action):
      pass

    def _get_reward(self):
      pass

    def render(self,mode='rgb_array'):
      pass