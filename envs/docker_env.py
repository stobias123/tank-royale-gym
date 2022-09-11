import gym
from gym import spaces
import numpy

from lib.dependency_managers.docker_manager import DockerManager


class BaseRobocodeEnv(gym.Env):

    metadata = {'render.modes': ['rgb_array']}

    def __init__(self):
        self.__version__ = "0.1.0"
        super(BaseRobocodeEnv, self).__init__()
        #logging.info(f"[BaseRobocodeEnv Env] - Version {self.__version__}")
        # Env Setup - WASD to integer.
        self.HEIGHT: int = 600
        self.WIDTH: int = 800
        self.action_space = spaces.Discrete(16)
        self.observation_space = spaces.Box(low=0, high=255,
                                        shape=(self.HEIGHT, self.WIDTH, 3), dtype=numpy.uint8)
        self.robocode_manager: DockerManager = DockerManager()
        self.robocode_manager.start()


    def reset(self):
        self.robocode_manager.reset()
        ## step to get 1 obs
        obs, reward, done, truncated, info = self.step(0)
        return obs



    def step(self, action):
        # Send our action
        obs = self.robocode_manager.step(action)
        #return self.last_frame, obs['reward'], obs['done'], obs['info']

    def _get_reward(self):
      pass

    def render(self,mode='rgb_array'):
      pass