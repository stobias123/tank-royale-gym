import logging
import random
import time

from tank_royal_manager.manager.controller_manager import ControllerManager

import docker
from docker import errors
from lib.bot_api.base_bot import BasicBot
from lib.bot_api.bots import FireBot, AgentBot, CustomBotManager
from lib.dependency_managers.docker_manager import DockerManager
from .base_env import BaseRobocodeEnv


class BooterEnv(BaseRobocodeEnv):
    metadata = {'render.modes': ['rgb_array']}

    def __init__(self):
        self.port = random.randint(7000, 8000)
        self.ws_address = f"ws://localhost:{self.port}"
        # start up the robocode server.
        self.robocode_manager: DockerManager = DockerManager(port_number=self.port)
        self.robocode_manager.start()

        time.sleep(2)
        self.bot_agent = AgentBot(self.ws_address)
        self.bot_connection_addr=f"ws://10.245.28.134:{self.port}"
        self.enemy_agent = BooterAgent(self.ws_address, ws_address=self.bot_connection_addr, port=self.port)

        self.HEIGHT: int = 600
        self.WIDTH: int = 800

        super().__init__()

        # Set up the controller
        self.controller = ControllerManager(self.ws_address)
        self.controller.start_thread()
    def reset(self):
        obs = super().reset()
        self.enemy_agent.reset()
        return obs


class BooterAgent(BasicBot):
    def __init__(self, conn_pw: str, ws_address: str = 'ws://localhost:7654', port: int = '7654'):
        self.booter_image = 'gcr.io/stobias-dev/tank-royal-booter:0.17.4'
        self.container = None
        self.conn_pw = conn_pw
        self.docker_client = docker.from_env()
        self.port = port
        self.container_name = f"tank-royal-booter-{self.port}"
        try:
            self.container = self.docker_client.containers.get(self.container_name)
            self.container.restart()
        except errors.NotFound as e:
            try:
                self.container = self.docker_client.containers.run(self.booter_image,
                                                                   name=self.container_name,
                                                                   detach=True,
                                                                   auto_remove=True,
                                                                   environment={
                                                                       "SERVER_URL": ws_address,
                                                                   },
                                                                   command=['run', '/sample_bots/TrackFire']
                                                                   )
                logging.info(f"Started container {self.container.id}")
                time.sleep(5)
            except:
                raise "Problem starting the container. Please ensure docker is running and the port is open."
        logging.info(f"[Tank Royal] Started Booter ")

    def handle_tick(self):
        pass

    def reset(self):
        self.container.restart()
