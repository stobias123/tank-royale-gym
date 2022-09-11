import threading
from time import sleep

import gym
import tank_royal_manager.manager.game_types
from gym import spaces
import numpy
from tank_royal_manager.manager.controller_manager import ControllerManager

from lib.bot_api.bot import Bot
from lib.dependency_managers.docker_manager import DockerManager


class DockerRobocodeEnv(gym.Env):

    metadata = {'render.modes': ['rgb_array']}

    def __init__(self):
        self.thread = None
        self.__version__ = "0.1.0"
        #logging.info(f"[BaseRobocodeEnv Env] - Version {self.__version__}")
        # Env Setup - WASD to integer.
        self.HEIGHT: int = 600
        self.WIDTH: int = 800
        self.action_space = spaces.Discrete(16)
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(self.HEIGHT, self.WIDTH, 3), dtype=numpy.uint8)
        self.robocode_manager: DockerManager = DockerManager()
        ## start up the robocode server.
        self.robocode_manager.start()

        ## Set up the controller
        self.controller = ControllerManager(ws_address='ws://localhost:7654')
        self.controller.start_thread()

        ## Start up our bot agent
        self.bot_agent = Bot()
        self.enemy_agent = Bot()

        # thread all our bots and contorller

    def reset(self):
        self.robocode_manager.reset()
        sleep(1)
        ## step to get 1 obs
        #obs, reward, done, truncated, info = self.step(0)



    def step(self, action):
        print(self.bot_agent.botManager.handler.bot_map)
        # Send our action
        obs = self.controller.step()
        sleep((tank_royal_manager.manager.game_types.STANDARD.turnTimeout / 1000000) + .01)
        #return self.last_frame, obs['reward'], obs['done'], obs['info']

    def _get_reward(self):
      pass

    def render(self,mode='rgb_array'):
      pass