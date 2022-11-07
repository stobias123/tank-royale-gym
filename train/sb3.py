import logging
import os
import sys
from argparse import ArgumentParser
from random import random
from random import randint
import boto3
import mlflow
import gym
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback, CallbackList

from wrappers import ResizeObservation, GrayScaleObservation

from tank_royal_gym.envs.booter_env_lite import BooterLiteEnv
from mlflow.tracking import MlflowClient

from stable_baselines3.common.vec_env import VecVideoRecorder, DummyVecEnv
from stable_baselines3 import A2C, PPO
from typing import Any, Optional, Tuple, Union,Dict
from collections import defaultdict
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.vec_env import SubprocVecEnv
import numpy as np
from stable_baselines3.common.logger import HumanOutputFormat, KVWriter, Logger

class MLflowOutputFormat(KVWriter):
    """
    Dumps key/value pairs into MLflow's numeric format.
    """

    def write(
        self,
        key_values: Dict[str, Any],
        key_excluded: Dict[str, Union[str, Tuple[str, ...]]],
        step: int = 0,
    ) -> None:

        for (key, value), (_, excluded) in zip(
            sorted(key_values.items()), sorted(key_excluded.items())
        ):

            if excluded is not None and "mlflow" in excluded:
                continue

            if isinstance(value, np.ScalarType):
                if not isinstance(value, str):
                    mlflow.log_metric(key, value, step)


loggers = Logger(
    folder=None,
    output_formats=[HumanOutputFormat(sys.stdout), MLflowOutputFormat()],
)
class NoopResetEnv(gym.Wrapper):
    """
    Sample initial states by taking random number of no-ops on reset.
    No-op is assumed to be action 0.

    :param env: the environment to wrap
    :param noop_max: the maximum value of no-ops to run
    """

    def __init__(self, env: gym.Env, noop_max: int = 10):
        gym.Wrapper.__init__(self, env)
        self.noop_max = noop_max
        self.override_num_noops = None
        self.noop_action = 0

    def reset(self, **kwargs) -> np.ndarray:
        self.env.reset(**kwargs)
        obs, _, done, _ = self.env.step(self.noop_action)
        for i in range(randint(1, self.noop_max)):
            obs, _, done, _ = self.env.step(self.noop_action)
        return obs

def record_video(model: str , env_id: str , policy_name: str, record_steps: int, video_folder: str = 'artifacts/'):
    video_length = record_steps

    env = DummyVecEnv([lambda: gym.make(env_id)])

    obs = env.reset()
    # Record the video starting at the first step
    env = VecVideoRecorder(env, video_folder,
                           record_video_trigger=lambda x: x == 0, video_length=video_length,
                           name_prefix=f"{policy_name}" + "-{}".format(env_id))
    env = GrayScaleObservation(env)
    env = ResizeObservation(env, shape=[240,320])
    env.reset()
    for _ in range(video_length + 1):
        action, _states = model.predict(obs)
        obs, _, _, _ = env.step(action)
    # Save the video
    env.close()


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
        env = ResizeObservation(env, shape=[84, 84])
        env = gym.wrappers.FrameStack(env, 4)
        return env
    return _init

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--timesteps", dest="timesteps", help="timesteps to run training for", default=1000, type=int)
    parser.add_argument("--record-timesteps", dest="record_timesteps", help="timesteps to run training for", default=1000, type=int)
    parser.add_argument("--policy", dest="policy", help="policy", default='MlpPolicy', type=str)
    parser.add_argument("--load-model", dest="load_model", help="stable baselines 3 model path to load - no .zip", default='', type=str)
    parser.add_argument("--env-id", dest="env_id", help="env to run.", default='BooterLiteEnv-v0', type=str)
    args = parser.parse_args()

    client = MlflowClient()
    mlflow.set_tracking_uri("https://mlflow.svc.bird.co/")

    logging.basicConfig(level=logging.INFO)
    env_id = args.env_id

    # foo
    runid = os.environ.get('MLFLOW_RUN_ID')
    if runid is None:
        experiment = mlflow.set_experiment(experiment_name="Robocode")
        runid = client.create_run(experiment.experiment_id).info.run_id

    s3_client = boto3.client('s3')
    s3_client.download_file('bird-mlflow-bucket', 'artifacts/5/a0d8b596975945329905301496b9420c/artifacts/a0d8b596975945329905301496b9420c/robocode-model.zip', 'robocode-model.zip')

    with mlflow.start_run(run_id=runid) as active_run:
        policy = args.policy
        artifact_uri = mlflow.get_artifact_uri()
        print(f"Artifact uri - {artifact_uri}")
        mlflow.pytorch.autolog()
        mlflow.log_params({
            "env": env_id,
            "model": PPO,
            "policy": policy,
            "timesteps": args.timesteps
        })
        ## Train - should take ~23 mins at 7FPS.
        env = SubprocVecEnv([make_env(env_id, i) for i in range(os.cpu_count()-2)])
        #env = make_env(env_id, 0)()
        if args.load_model == '':
            model = PPO(policy, env, verbose=1, tensorboard_log="/tensorboard")
        else:
            logging.info(f"[Pipeline] Loading model.... {args.load_model}")
            model= PPO.load(args.load_model, env=env)
        model.set_logger(loggers)

        eval_env = DummyVecEnv([lambda: make_env(args.env_id, 9, 11)()])
        eval_callback = EvalCallback(eval_env, best_model_save_path="/tensorboard/eval_models/",
                             log_path="/tensorboard/eval_logs/", eval_freq=1000,
                             deterministic=True, render=False)

        checkpoint_callback = CheckpointCallback(save_freq=5000, save_path="/tensorboard/checkpoints/")
        callback = CallbackList([checkpoint_callback, eval_callback])

        model.learn(total_timesteps=args.timesteps, callback=callback)
        model.save(f"artifacts/models/{active_run.info.run_id}/robocode-model")
        uri = mlflow.get_artifact_uri()
        mlflow.log_artifacts(f"artifacts/models/")


        video_env = DummyVecEnv([lambda: make_env(args.env_id, 10, 23)()])
        video_env = VecVideoRecorder(env, f"artifacts/videos/{active_run.info.run_id}",
                           record_video_trigger=lambda x: x == 0, video_length=args.record_timesteps,
                           name_prefix=f"agent-{args.env_id}")
        obs = env.reset()
        for _ in range(args.record_timesteps + 1):
            action = model.predict(obs,deterministic=True)
            obs, _, _, _ = video_env.step(action)
        video_env.close()

        mlflow.log_artifacts(f"artifacts/videos/")
        mlflow.log_artifacts(f"/tensorboard/")

        exit(0)


        #walks = os.walk('/artifacts/videos')

        #for source, dirs, files in walks:
        #    for filename in files:
        #        local_file = os.path.join(source, filename)
        #        s3_client.upload_file(local_file,
        #                              "mlflow-s3-bucket",
        #                              f"videos/{local_file[1:]}")
        #mlflow.log_artifacts('/artifacts/videos')
        #print(f"Trying to find the mlflow videos from my current dir.")