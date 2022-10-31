import logging
import os
from random import randint
import time
from kubernetes import client, config, watch
from .robocode_manager import RobocodeManager


class K8sManager(RobocodeManager):
    def __init__(self,  namespace: str = "robocode", port_number=7654, robocode_image: str = 'gcr.io/stobias-dev/tank-royal-server:0.17.6'):
        super().__init__(port_number=port_number, robocode_image=robocode_image)
        print("loading in cluster config")
        if os.environ.get('KUBECONFIG') == None:
            config.load_incluster_config()
        else:
            config.load_config()
        self.v1_client = client.CoreV1Api()
        self.conn_pw = 'abc123'
        self.namespace = namespace
        self.port_number = port_number
        self.ip = None
        self.pod_name = f"robocode-training-{randint(1,10000)}"
        self.pod_labels = {"app": "robocode", "instance": self.pod_name}

    # docker run -it --net=host -d --name robocode stobias123/robocode
    def start(self):
        logging.info(f"[Tank Royale] Starting Robocode on port {self.port_number}")
        self.ip = self.create_robocode_game()
        time.sleep(5)
        logging.info(f"[Tank Royale] Started Robocode on port {self.port_number}")

    def create_robocode_game(self, name: str ="train"):
        metadata = client.V1ObjectMeta(generate_name=self.pod_name, labels=self.pod_labels)
        container = client.V1Container(
            image=self.robocode_image,
            name=name,
            image_pull_policy='Always',
            ports=[client.V1ContainerPort(
                container_port=self.port_number
            )],
            # args=[],
            args=['-C', self.conn_pw, '-p', str(self.port_number)]
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
            logging.info(f"[Tank Royale] Checking for pod.")
            pod = self.v1_client.list_namespaced_pod(label_selector=f"instance={self.pod_name}",
                                                          namespace=self.namespace).items[0]
            time.sleep(1)
        logging.info(f"[Tank Royale] Started Robocode at IP {pod.status.pod_ip}")
        return pod.status.pod_ip

    def get_robocode_pod(self):
        pod_list = self.v1_client.list_namespaced_pod(label_selector=f"app={self.pod_name}",
                                                          namespace=self.namespace)
        if len(pod_list.items) < 1:
            return None
        if len(pod_list.items) > 1:
            raise "There's a problem, we got too many pods"
        return pod_list.items[0]

    def stop(self):
        self.v1_client.delete_namespaced_pod(name=self.pod_name, namespace=self.namespace)