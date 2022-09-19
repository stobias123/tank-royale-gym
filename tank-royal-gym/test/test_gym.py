import logging
import sys
from time import sleep

import gym
from gym import wrappers

from envs.docker_env import DockerRobocodeEnv

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
def test_env():
    testenv = DockerRobocodeEnv()
    testenv.reset()
    sleep(1)
    for i in range(0,500):
        testenv.step(0)
    print("done")
