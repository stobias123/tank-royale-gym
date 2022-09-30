import random

from tank_royal_manager.manager.controller_manager import ControllerManager

from lib.bot_api.bots import FireBot, AgentBot
from lib.dependency_managers.docker_manager import DockerManager
from .base_env import BaseRobocodeEnv


class HalfSizeEnv(BaseRobocodeEnv):
    metadata = {'render.modes': ['rgb_array']}

    def __init__(self):
        self.port = random.randint(7000, 8000)
        self.ws_address = f"ws://localhost:{self.port}"
        # start up the robocode server.
        self.robocode_manager: DockerManager = DockerManager(port_number=self.port)
        self.robocode_manager.start()

        self.bot_agent = AgentBot(self.ws_address)
        self.enemy_agent = FireBot(self.ws_address)

        super().__init__()
        self.HEIGHT = 300
        self.WIDTH = 400

        # Set up the controller
        self.controller = ControllerManager(self.ws_address)
        self.controller.start_thread()
