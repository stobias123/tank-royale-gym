from time import sleep

from envs.docker_env import DockerRobocodeEnv


def test_env():
    testenv = DockerRobocodeEnv()
    testenv.reset()
    sleep(1)
    for i in range(0,500):
        testenv.step(0)
    print("done")
