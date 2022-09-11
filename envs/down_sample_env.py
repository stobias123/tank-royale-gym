import logging
from gym_robocode.envs import RobocodeV2
from gym_robocode.envs.lib.robocode_manager import RobocodeManager
from gym_robocode.envs.lib.connection_manager import ConnectionManager
from random import randint
import numpy
from PIL import Image
from gym import spaces
import cv2


class RobocodeDownSample(RobocodeV2):
    """
    Robocodev2 environment spawns a new headless robocode for every instantiation.
    """

    def __init__(self):
        logging.info(f"[RobocdeDownSampleEnv] - Version 2.1")
        logging.basicConfig(level=logging.INFO)
        super(RobocodeDownSample, self).__init__()
        self.last_frame = None
        self.episode_over = False
        scale_percent = 60  # percent of original size
        self.down_width = int(self.WIDTH * scale_percent / 100)
        self.down_height = int(self.HEIGHT * scale_percent / 100)
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(self.down_height, self.down_width, 3), dtype=numpy.uint8)

    def step(self, action):
        # Send our action
        obs = self.connection_manager.step(action)
        self.episode_over = obs['done']
        self.last_frame = self.connection_manager.obsAsNumpyArray(
            obs['observation'])
        obs, reward, done, info = self.last_frame, obs['reward'], obs['done'], obs['info']
        obs = cv2.resize(
            obs , (self.down_width, self.down_height), interpolation=cv2.INTER_AREA
        )
        return obs, reward, done, info

    def _get_reward(self):
        pass

    def render(self, mode='rgb_array'):
        return self.last_frame