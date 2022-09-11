import logging
import rel
import threading
import time
import docker
from docker import errors
from tank_royal_manager.manager import ControllerManager

from lib.dependency_managers.robocode_manager import RobocodeManager

class DockerManager(RobocodeManager):
    """
    DockerManager is an instance of robocodemanager that is helpful for running things locally.
    """
    def __init__(self, port_number: int = 7654, conn_pw: str ='abc123'):
        self.docker_client = docker.from_env()
        self.port_number = port_number
        self.robocode_image = 'gcr.io/stobias-dev/tank-royal-server:latest-debug'
        self.container = None
        self.conn_pw = conn_pw
        self.container_name = 'tank-royal-server'

    # docker run -it --net=host -d --name robocode stobias123/robocode
    def start(self):
        logging.info(f"[Tank Royal] Starting Robocode on port {self.port_number}")
        try:
            self.container = self.docker_client.containers.get(self.container_name)
            self.container.restart()
        except errors.NotFound as e:
            try:
                self.container = self.docker_client.containers.run(self.robocode_image,
                                                                   name=self.container_name,
                                                                   detach=True,
                                                                   auto_remove=True,
                                                                   ports={
                                                                       7654: self.port_number
                                                                   },
                                                                   command=['-C', self.conn_pw, '-p', str(self.port_number)]
                                                                   )
                logging.info(f"Started container {self.container.id}")
                time.sleep(5)
            except:
                raise "Problem starting the container. Please ensure docker is running and the port is open."
        logging.info(f"[Tank Royal] Started Robocode on port {self.port_number}")

    def stop(self):
        self.container.stop()

    def reset(self):
        try:
            self.container.restart()
        except:
            raise "Problem restarting container"
