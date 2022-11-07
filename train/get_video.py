import sys
import gym
import logging
from argparse import ArgumentParser

from gym.wrappers import FrameStack
from gym.wrappers.monitoring.video_recorder import VideoRecorder

from wrappers import ResizeObservation, GrayScaleObservation
from stable_baselines3.common.vec_env import VecVideoRecorder, DummyVecEnv
from stable_baselines3 import A2C, PPO
from tank_royal_gym.envs.booter_env_lite import BooterLiteEnv


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def make_env(env_id, rank, seed=0):
    """
    Utility function for multiprocessed env.

    :param env_id: (str) the environment ID
    :param num_env: (int) the number of environments you wish to have in subprocesses
    :param seed: (int) the inital seed for RNG
    :param rank: (int) index of the subprocess
    """
    def _init():
        env = gym.make(env_id)
        env = GrayScaleObservation(env)
        env = ResizeObservation(env, shape=[240,320])
        env = FrameStack(env, num_stack=4)
        env.seed(seed + rank)
        return env
    return _init

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--record-timesteps", dest="record_timesteps", help="timesteps to run training for", default=1000, type=int)
    parser.add_argument("--load-model", dest="load_model", help="stable baselines 3 model path to load - no .zip", default='', type=str)
    parser.add_argument("--env-id", dest="env_id", help="env to run.", default='BooterLiteEnv-v0', type=str)
    args = parser.parse_args()

    # env
    #env = gym.make(args.env_id)

    polic_name = "PPO"
    video_folder = f"artifacts/videos/"
    video_name = "video.mp4"

    env = DummyVecEnv([lambda: make_env(args.env_id, 0)()])
    env = VecVideoRecorder(env, video_folder,
                       record_video_trigger=lambda x: x == 0, video_length=args.record_timesteps,
                       name_prefix=f"agent-{args.env_id}")

    model = PPO.load(args.load_model, env=env)
    obs = env.reset()
    for _ in range(args.record_timesteps + 1):
        action = model.predict(obs)
        obs, _, _, _ = env.step(action)
    env.close()
