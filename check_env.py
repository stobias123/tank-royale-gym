import ray
from ray.rllib import utils
import logging
import sys
from time import sleep

import gym

from envs.booter_env import BooterEnv
from envs.docker_env import DockerRobocodeEnv
from envs.kubernetes_env import KubernetesRobocodeEnv


env = BooterEnv()

utils.check_env(env)