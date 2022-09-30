import logging
import sys
from time import sleep

import easy_run

from envs.booter_env import BooterEnv
from envs.docker_env import DockerRobocodeEnv
from envs.kubernetes_env import KubernetesRobocodeEnv

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

if __name__ == "__main__":
    testenv = BooterEnv()
    testenv.reset()
    sleep(1)
    for i in range(0,500):
        obs, reward, done, info = testenv.step(0)
        if done:
            break
    print("done")
