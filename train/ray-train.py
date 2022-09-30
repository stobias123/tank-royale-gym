# Import the RL algorithm (Algorithm) we would like to use.
import datetime
from typing import Dict

import gym
import numpy as np
from gym.wrappers import FrameStack
from ray.rllib.algorithms.ppo import PPO
from ray.tune.registry import register_env
from ray.rllib.agents.callbacks import DefaultCallbacks
from ray.rllib.env import BaseEnv
from ray.rllib.policy import Policy
from ray.rllib.policy.sample_batch import SampleBatch
from ray.rllib.evaluation import MultiAgentEpisode, RolloutWorker
from ray.rllib.agents.callbacks import DefaultCallbacks


from wrappers import SkipFrame, GrayScaleObservation, ResizeObservation


# noinspection PyPackageRequirements
def env_creator(env_config):
    from envs.booter_env import BooterEnv
    env = gym.make('BooterEnv-v0')  # return an env instance
    env = GrayScaleObservation(env)
    env = ResizeObservation(env, shape=[240,320])
    return env

class MyCallbacks(DefaultCallbacks):
    def on_episode_step(self, worker: RolloutWorker, base_env: BaseEnv,
                        episode: MultiAgentEpisode, **kwargs):
        info = episode.last_info_for()
        last_action = episode.last_action_for()
        if info is not None: # why None??
            net_worth = info['net_worth']
            episode.user_data["net_worth"].append(net_worth)

    def on_episode_end(self, worker: RolloutWorker, base_env: BaseEnv,
           policies: Dict[str, Policy], episode: MultiAgentEpisode,
                       **kwargs):
        pole_angle = np.mean(episode.user_data["pole_angles"])
        print("episode {} ended with length {} and pole angles {}".format(
            episode.episode_id, episode.length, pole_angle))
        episode.custom_metrics["pole_angle"] = pole_angle
        episode.hist_data["pole_angles"] = episode.user_data["pole_angles"]

register_env("BooterEnv-v0", env_creator)

# Configure the algorithm.
config = {
    # Environment (RLlib understands openAI gym registered strings).
    "env": "BooterEnv-v0",
    # Use 2 environment workers (aka "rollout workers") that parallelly
    # collect samples from their own environment clone(s).
    "num_workers": 4,
    # Change this to "framework: torch", if you are using PyTorch.
    # Also, use "framework: tf2" for tf2.x eager execution.
    "framework": "torch",
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

# Create our RLlib Trainer.
algo = PPO(config=config)

# Run it for n training iterations. A training iteration includes
# parallel sample collection by the environment workers as well as
# loss calculation on the collected batch and a model update.
results = []
for i in range(77):
    print(f"{datetime.datetime.now()} starting iteration {i}")
    run = algo.train()
    results.append(run)
    if i % 25 == 0:
        algo.save("checkpoints")
    print(f"{datetime.datetime.now()} finished iteration {i}")

# Evaluate the trained Trainer (and render each timestep to the shell's
# output).
algo.evaluate()
print("Training completed. Results:", results)
