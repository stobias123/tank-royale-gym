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
        self.bot_connection_addr=f"ws://192.168.1.16:{self.port}"
        self.enemy_agent = BooterAgent(self.ws_address, ws_address=self.bot_connection_addr)

        self.HEIGHT = 300
        self.WIDTH = 400

        super().__init__()

        # Set up the controller
        self.controller = ControllerManager(self.ws_address)
        self.controller.start_thread()
    def reset(self):
        super().reset()
        self.enemy_agent.reset()


class BooterAgent(BasicBot):
    def __init__(self, conn_pw: str, ws_address: str = 'ws://localhost:7654'):
        self.booter_image = 'gcr.io/stobias-dev/tank-royal-booter:latest'
        self.container = None
        self.conn_pw = conn_pw
        self.docker_client = docker.from_env()
        self.container_name = f"tank-royal-booter-{random.randint(0, 100000)}"
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
