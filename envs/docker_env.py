import logging
import threading
from time import sleep

import gym
import tank_royal_manager.manager.game_types
from gym import spaces
import numpy
from tank_royal_manager.manager.controller_manager import ControllerManager
from tank_royal_manager.robocode_event_models import TickEventForObserver

from lib.bot_api.bots import DriveAndScanBot, FireBot, BasicBot
from lib.dependency_managers.docker_manager import DockerManager
from lib.render.basic_rgb import BasicRGB


class DockerRobocodeEnv(gym.Env):
    metadata = {'render.modes': ['rgb_array']}

    def __init__(self):
        self.thread = None
        self.__version__ = "0.1.0"
        # logging.info(f"[BaseRobocodeEnv Env] - Version {self.__version__}")
        # Env Setup - WASD to integer.
        self.HEIGHT: int = 600
        self.WIDTH: int = 800
        self.render_mode = "rgb_array"
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(self.HEIGHT, self.WIDTH, 3), dtype=numpy.uint8)
        self.robocode_manager: DockerManager = DockerManager()
        ws_address = 'ws://localhost:7654'

        # start up the robocode server.
        self.robocode_manager.start()

        # Set up the controller
        self.controller = ControllerManager(ws_address)
        self.controller.start_thread()

        # Start up our bot agent
        self.bot_agent = DriveAndScanBot(ws_address)
        self.enemy_agent = FireBot(ws_address)

        # Renderer
        self.renderer = BasicRGB(map_height=self.HEIGHT, map_width=self.WIDTH)

    def _get_frame(self):
        return self.renderer.draw_tick(tick_event=self.bot_agent.last_tick)

    def _get_reward(self, prev_state: TickEventForObserver, next_state: TickEventForObserver):
        for event in prev_state:
            pass


    def _is_done(self):
        pass

    def reset(self):
        self.robocode_manager.reset()
        sleep(1)
        ## step to get 1 obs
        # obs, reward, done, truncated, info = self.step(0)

    def step(self, action):
        # Send our action
        self.bot_agent.action_to_intent(action)
        self.controller.step()
        sleep((tank_royal_manager.manager.game_types.STANDARD.turnTimeout / 1000000) + .01)
        return self._get_frame(), self._get_reward(), self._is_done(), {}, {}

    def _get_reward(self):
        pass

    def render(self, mode='rgb_array'):
        return self._get_frame()
