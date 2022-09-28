import sys
from time import sleep

from lib.dependency_managers.docker_manager import DockerManager
from lib.dependency_managers.k8s_manager import K8sManager


## Set our logging config to stdout and info

def test_docker_manager():
    manager = DockerManager()
    manager.start()
    sleep(15)
    manager.reset()
    sleep(15)
    manager.stop()
def test_docker_manager_step():
    manager = DockerManager()
    manager.start()
    sleep(15)
    manager.step()
    print('test')

def test_k8s_manager():
    import logging
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    manager = K8sManager()
    manager.start()
    for i in range(0, 10):
        manager.step()