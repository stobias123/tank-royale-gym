import logging
import sys
from time import sleep

import gym
from gym import wrappers

from envs.docker_env import DockerRobocodeEnv
from lib.bot_api.bots import AgentBot

gym.envs.register(
    id='DockerRobocodeEnv-v0',
    entry_point='envs.docker_env:DockerRobocodeEnv',
    max_episode_steps=1000,
)

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    env = gym.make('DockerRobocodeEnv-v0')
    env = wrappers.RecordVideo(env, "./gym-results")
    env.reset()
    sleep(5)
    for i in range(0, 500):
        action = env.action_space.sample()
        next_state, reward, terminated, trunc, info = env.step(action)
    env.close()
