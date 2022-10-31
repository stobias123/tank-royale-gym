import logging
import os
import random
import time
import rel

from tank_royal_manager.manager.controller_manager import ControllerManager

from kubernetes import client, config, watch

import docker
from docker import errors
from lib.bot_api.base_bot import BasicBot
from lib.bot_api.bots import FireBot, AgentBot, CustomBotManager
from lib.dependency_managers.docker_manager import DockerManager
from lib.dependency_managers.k8s_manager import K8sManager
from .base_env import BaseRobocodeEnv


class BooterLiteEnv(BaseRobocodeEnv):
    metadata = {'render.modes': ['rgb_array']}

    def __init__(self):
        self.port = random.randint(7000, 8000)
        self.robocode_manager: K8sManager = K8sManager(port_number=self.port)
        # start up the robocode server.
        self.robocode_manager.start()
        self.server_url = f"ws://{self.robocode_manager.ip}:{self.port}"
        self.bot_agent = AgentBot(ws_address=self.server_url)
        self.enemy_agent = BooterLiteAgent(conn_pw="abc123", ws_address=self.server_url, port=self.port)

        self.HEIGHT: int = 600
        self.WIDTH: int = 800

        super().__init__()

        # Set up the controller
        self.controller = ControllerManager(self.server_url)
        self.controller.start_thread()

    def reset(self):
        logging.warning("[BooterEnvLite] - Resetting")
        self.controller.game_over = False
        self.controller.reset_turn = True
        #logging.warning("[BooterEnvLite] - Stopping")
        #self.controller.stop()
        #time.sleep(.05)
        logging.warning("[BooterEnvLite] - Ending Round")
        self.controller.end_round()
        time.sleep(.05)
        logging.warning("[BooterEnvLite] - Starting Round")
        self.controller.start()
        time.sleep(.05)
        obs = self.step(0)
        return obs[0]


class BooterLiteAgent(BasicBot):
    def __init__(self, conn_pw: str, ws_address: str = 'ws://localhost:4567', port: int = 4567, namespace='robocode'):
        self.ip = None
        self.booter_image = 'gcr.io/stobias-dev/tank-royal-booter-full:0.17.4'
        if os.environ.get('KUBECONFIG') == None:
            print("[BooterLiteAgent] loading in cluster config")
            config.load_incluster_config()
        else:
            print("[BooterLiteAgent] Using Kube Context")
            config.load_config()
        self.v1_client = client.CoreV1Api()
        self.namespace = namespace
        self.ws_address = ws_address
        self.container = None
        self.conn_pw = conn_pw
        self.port = port
        self.pod_name = f"tank-royal-booter-{self.port}-{random.randint(0, 100000)}"
        self.pod_labels = {"app": "robocode-booter", "instance": self.pod_name}
        self.start()


    def handle_tick(self):
        pass

    def reset(self):
        logging.warning("[BooterLiteEnv] Should be resetting the booter.")

    def start(self):
        logging.info(f"[BooterLiteEnv] Starting Robocode on port {self.port}")
        self.ip = self.create_booter_pod()
        time.sleep(5)
        logging.info(f"[BooterLiteEnv] Started Robocode on port {self.port}")

    def create_booter_pod(self, name: str = "train"):
        metadata = client.V1ObjectMeta(generate_name=self.pod_name, labels=self.pod_labels)
        container = client.V1Container(
            image=self.booter_image,
            name=name,
            image_pull_policy='Always',
            ports=[client.V1ContainerPort(
                container_port=self.port
            )],
            working_dir="/sample_bots/TrackFire",
            command=["/bin/bash"],
            env=[
                client.V1EnvVar(name="SERVER_URL", value=self.ws_address),
                client.V1EnvVar(name="SERVER_SECRET", value=self.conn_pw),
                ],
            args=['-c', "java -cp ../lib/* TrackFire.java"]
        )
        pod = client.V1Pod(
            spec=client.V1PodSpec(
                restart_policy="Never",
                containers=[container]
            ),
            metadata=client.V1ObjectMeta(name=self.pod_name, labels=self.pod_labels),
        )
        pod = self.v1_client.create_namespaced_pod(namespace=self.namespace, body=pod)
        pod_list = self.v1_client.list_namespaced_pod(label_selector=f"instance={self.pod_name}",
                                                      namespace=self.namespace)
        pod = pod_list.items[0]
        while pod.status.pod_ip == None:
            logging.info(f"[BooterLiteEnv] Checking for pod.")
            pod = self.v1_client.list_namespaced_pod(label_selector=f"instance={self.pod_name}",
                                                     namespace=self.namespace).items[0]
            time.sleep(1)
        logging.info(f"[BooterLiteEnv] Started Trackfire agent at IP {pod.status.pod_ip}")
        return pod.status.pod_ip

    def get_robocode_pod(self):
        pod_list = self.v1_client.list_namespaced_pod(label_selector=f"instance={self.pod_name}",
                                                      namespace=self.namespace)
        if len(pod_list.items) < 1:
            return None
        if len(pod_list.items) > 1:
            raise "There's a problem, we got too many pods"
        return pod_list.items[0]

    def stop(self):
        self.v1_client.delete_namespaced_pod(name=self.pod_name, namespace=self.namespace)
