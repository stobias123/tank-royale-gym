import argparse
import easy_run
import os

import ray
from ray import air, tune
from envs.half_size_env import HalfSizeEnv
from ray.tune.registry import register_env
from wrappers import *
from easy_run.wrappers import FrameStack
from ray.rllib.algorithms.ppo import PPO

print("Training completed. Restoring new Trainer for action inference.")
# Get the last checkpoint from the above training run.
# Create new Trainer and restore its state from the last checkpoint.
config = {
    "env": "HalfSampleEnv-v0",
    # Use GPUs iff `RLLIB_NUM_GPUS` env var set to > 0.
    "num_gpus": int(os.environ.get("RLLIB_NUM_GPUS", "0")),
    "framework": "torch",
    "num_workers": 1,
    # Change this to "framework: torch", if you are using PyTorch.
    # Also, use "framework: tf2" for tf2.x eager execution.
    # Tweak the default model provided automatically by RLlib,
    # given the environment's observation- and action spaces.
    "model": {
        "fcnet_hiddens": [84, 84],
        "fcnet_activation": "relu",
    },
    # Set up a separate evaluation worker set for the
    # `algo.evaluate()` call after training (see below).
    "evaluation_num_workers": 1,
    # Only for evaluation runs, render the env.
    "evaluation_config": {
        "render_env": True,
    },
    "logger_config": {
        "logdir": "./ray_results",
    }
}

def env_creator(env_config):
    from envs.half_size_env import HalfSizeEnv
    env = gym.make('HalfSampleEnv-v0')  # return an env instance
    env = GrayScaleObservation(env)
    env = ResizeObservation(env, shape=[84,84])
    return env

register_env("HalfSampleEnv-v0", env_creator)

algo=PPO(config=config)
algo.restore('/Users/steven.tobias/repos/misc_projects/tank-royal-gym/train/checkpoints/checkpoint_000076/checkpoint-76')

# # Apply Wrappers to environment
env = gym.make('HalfSampleEnv-v0')
env = GrayScaleObservation(env)
env = ResizeObservation(env, shape=84)
obs = env.reset()

num_episodes = 0
episode_reward = 0.0

while num_episodes < 1000:
    # Compute an action (`a`).
    a = algo.compute_single_action(
        observation=obs,
        explore=False,
        policy_id="default_policy",
    )
    # Send the computed action `a` to the env.
    print(a)
    obs, reward, done, _ = env.step(a)
    episode_reward += reward
    # Is the episode `done`? -> Reset.
    if done:
        print(f"Episode done: Total reward = {episode_reward}")
        obs = env.reset()
        num_episodes += 1
        episode_reward = 0.0