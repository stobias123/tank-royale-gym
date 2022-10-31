import logging
import random
import time
import rel

from tank_royal_manager.manager.controller_manager import ControllerManager

import docker
from docker import errors
from lib.bot_api.base_bot import BasicBot
from lib.bot_api.bots import FireBot, AgentBot, CustomBotManager
from lib.dependency_managers.docker_manager import DockerManager
from lib.dependency_managers.k8s_manager import K8sManager
from .base_env import BaseRobocodeEnv


class BooterLiteEnv(BaseRobocodeEnv):
    metadata = {'render.modes': ['rgb_array']}

    def __init__(self):
        self.port = random.randint(7000, 8000)
        self.robocode_manager: K8sManager = K8sManager(port_number=port)
        # start up the robocode server.
        self.robocode_manager.start()
        ws_address = f"ws://{self.robocode_manager.ip}:{port}"
        self.bot_agent = AgentBot(ws_address=self.server_url)
        self.enemy_agent = BooterLiteAgent(conn_pw="abc123", ws_address=self.server_url, port=self.port)

        self.HEIGHT: int = 600
        self.WIDTH: int = 800

        super().__init__()

        # Set up the controller
        self.controller = ControllerManager(self.server_url)
        self.controller.start_thread()

    def reset(self):
        self.controller.game_over = False
        self.controller.reset_turn = True
        self.controller.stop()
        self.controller.end_round()
        self.controller.start()
        time.sleep(.05)
        obs = self.step(0)
        return obs


class BooterLiteAgent(BasicBot):
    def __init__(self, conn_pw: str, ws_address: str = 'ws://localhost:4567', port: int = 4567):
        self.booter_image = 'gcr.io/stobias-dev/tank-royal-booter-full:0.17.4'
        self.container = None
        self.conn_pw = conn_pw
        self.docker_client = docker.from_env()
        self.port = port
        self.container_name = f"tank-royal-booter-{self.port}-{random.randint(0, 100000)}"
        try:
            self.container = self.docker_client.containers.get(self.container_name)
            self.container.restart()
        except errors.NotFound as e:
            try:
                self.container = self.docker_client.containers.run(self.booter_image,
                                                                   name=self.container_name,
                                                                   detach=True,
                                                                   environment={
                                                                       "SERVER_URL": ws_address,
                                                                   },
                                                                   working_dir="/sample_bots/TrackFire",
                                                                   entrypoint=["/bin/bash"],
                                                                   command=['-c', "java -cp ../lib/* TrackFire.java"]
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
