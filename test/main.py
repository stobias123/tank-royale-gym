from time import sleep

from tank_royal_manager.manager import STANDARD_GAME_TYPE

from envs.docker_env import DockerRobocodeEnv


if __name__ == "__main__":
    testenv = DockerRobocodeEnv()
    testenv.reset()
    sleep(1)
    for i in range(0, 450):
        testenv.step(0)
        sleep((STANDARD_GAME_TYPE.turnTimeout / 1000000) + .01)
    print("done")