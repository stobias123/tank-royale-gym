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


class BaseRobocodeEnv(gym.Env):
    metadata = {'render.modes': ['rgb_array']}

    def __init__(self):
        self.thread = None
        self.__version__ = "0.1.0"
        # logging.info(f"[BaseRobocodeEnv Env] - Version {self.__version__}")
        # Env Setup - WASD to integer.
        self.HEIGHT: int = 600
        self.WIDTH: int = 800
        self.step_count = 0
        self.prev_state = None
        self.action_space = spaces.Discrete(16)
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(self.HEIGHT, self.WIDTH, 3), dtype=numpy.uint8)
        self.port = random.randint(7000, 8000)
        self.ws_address = f"ws://localhost:{self.port}"

        # start up the robocode server.
        self.robocode_manager.start()

        # Set up the controller
        self.controller = ControllerManager(self.ws_address)
        self.controller.start_thread()
        # Renderer
        self.renderer = BasicRGB(map_height=self.HEIGHT, map_width=self.WIDTH)

        ## Reward settings
        self.turn_reward = 0.01
        self.hit_penalty = -0.03
        self.dealth_penalty = -100
        self.bullet_hit_reward = 100

    def _get_frame(self):
        #return self.renderer.draw_tick(tick_event=self.bot_agent.last_tick, bots=self.bot_agent.bots)
        return self.renderer.draw_tick(tick_event=self.bot_agent.last_tick, bots=self.bot_agent.bots)


    def _get_reward(self, prev_state: TickEventForBot, next_state: TickEventForBot) -> float:
        total_reward = 0.0
        total_reward += self.turn_reward
        if prev_state is None:
            return total_reward
        for event in next_state.events:
            if 'type' in event:
                if (event['type'] == MessageType.HitByBulletEvent or event['type'] == MessageType.BotHitWallEvent):
                    total_reward += self.hit_penalty
                if (event['type'] == MessageType.BotDeathEvent):
                    total_reward += self.dealth_penalty
                if (event['type'] == MessageType.BulletHitBotEvent):
                    total_reward += self.bullet_hit_reward
        return total_reward

    def _is_done(self):
        return self.controller.game_over

    def reset(self):
        self.robocode_manager.reset()
        sleep(10)
        self.controller.game_over = False
        ## step to get 1 obs
        obs, reward, done, info = self.step(0)
        return obs

    def step(self, action):
        # Send our action
        self.bot_agent.action_to_intent(action)
        self.controller.step()
        sleep((tank_royal_manager.manager.game_types.STANDARD.turnTimeout / 1000000) + .01)
        self.step_count += 1
        reward, done, info = self._get_reward(self.prev_state, self.bot_agent.last_tick), self._is_done(), {}
        self.prev_state = self.bot_agent.last_tick
        return self._get_frame(), reward, done, info

    def render(self, mode='rgb_array'):
        return self._get_frame()
