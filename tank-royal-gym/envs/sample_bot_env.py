import logging
import random
import threading
from time import sleep

import gym
import tank_royal_manager.manager.game_types
from PIL import Image
from gym import spaces
import numpy
from tank_royal_manager.manager.controller_manager import ControllerManager
from tank_royal_manager.robocode_event_models import TickEventForObserver, TickEventForBot, MessageType

from lib.bot_api.bots import DriveAndScanBot, FireBot, BasicBot, AgentBot
from lib.dependency_managers.docker_manager import DockerManager
from lib.render.basic_rgb import BasicRGB
import random
import torch
from base_env import BaseRobocodeEnv


class BaseRobocodeEnv(BaseRobocodeEnv):
    metadata = {'render.modes': ['rgb_array']}

    def __init__(self):
        super().__init__(self)
        self.robocode_manager: DockerManager = DockerManager(port_number=self.port)
