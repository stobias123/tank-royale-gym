import logging
import time


class RobocodeManager:

    def __init__(self, port_number: int = 7654, robocode_image: str = 'gcr.io/stobias-dev/robocode:1.3.4'):
        self.robocode_image: str = robocode_image
        self.port_number: int = None

    def start(self):
        pass

    def stop(self):
        pass

    def reset(self):
        pass

    def step(self):
        pass