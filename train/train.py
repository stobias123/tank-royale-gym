import logging
import sys
from datetime import datetime
from pathlib import Path
from time import sleep
from gym.wrappers import FrameStack
from agent import Agent
from metrics import MetricLogger
from wrappers import *
from envs.docker_env import DockerRobocodeEnv

# Apply Wrappers to environment
env = gym.make('DockerRobocodeEnv-v0')
sleep(1)
env = SkipFrame(env, skip=4)
env = GrayScaleObservation(env)
env = ResizeObservation(env, shape=84)
env = FrameStack(env, num_stack=4)
state = env.reset()

use_cuda = torch.cuda.is_available()
print(f"Using CUDA: {use_cuda}")
print()

save_dir = Path("checkpoints") / datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
save_dir.mkdir(parents=True)

mario = Agent(state_dim=(4, 84, 84), action_dim=env.action_space.n, save_dir=save_dir)

logger = MetricLogger(save_dir)
sleep(5)

## Configure logging library to log to stdout and log level info
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
episodes = 1000
for e in range(episodes):
    logging.info("Episode: %d" % e)
    print("Episode Start")

    state = env.reset()

    # Play the game!
    while True:

        # Run agent on the state
        action = mario.act(state)

        # Agent performs action
        next_state, reward, done, info = env.step(action)

        # Remember
        mario.cache(state, next_state, action, reward, done)

        # Learn
        q, loss = mario.learn()

        # Logging
        logger.log_step(reward, loss, q)

        # Update state
        state = next_state

        # Check if end of game
        if done:
            break

    logger.log_episode()
    print("Episode Complete")

    if e % 20 == 0:
        logger.record(episode=e, epsilon=mario.exploration_rate, step=mario.curr_step)

print("training complete")