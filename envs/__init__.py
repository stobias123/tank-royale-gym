import gym

from .docker_env import DockerRobocodeEnv

gym.envs.register(
    id='DockerRobocodeEnv-v0',
    entry_point='envs.docker_env:DockerRobocodeEnv',
    max_episode_steps=1000,
)