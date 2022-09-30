import gym

from .docker_env import DockerRobocodeEnv

gym.envs.register(
    id='DockerRobocodeEnv-v0',
    entry_point='envs.docker_env:DockerRobocodeEnv',
    max_episode_steps=1000,
)

gym.envs.register(
    id='KubernetesRobocodeEnv-v0',
    entry_point='envs.kubernetes_env:KubernetesRobocodeEnv',
    max_episode_steps=1000,
)

gym.envs.register(
    id='HalfSampleEnv-v0',
    entry_point='envs.half_size_env:HalfSizeEnv',
    max_episode_steps=1000,
)


gym.envs.register(
    id='BooterEnv-v0',
    entry_point='envs.booter_env:BooterEnv',
    max_episode_steps=1000,
)