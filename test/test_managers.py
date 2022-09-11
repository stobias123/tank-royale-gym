from time import sleep

from lib.dependency_managers.docker_manager import DockerManager


def test_docker_manager():
    manager = DockerManager()
    manager.start()
    sleep(15)
    manager.reset()
    sleep(15)
    manager.stop()
