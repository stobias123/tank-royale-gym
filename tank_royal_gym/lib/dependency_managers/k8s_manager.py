import logging
import os
from random import randint
import time
from kubernetes import client, config, watch
from .robocode_manager import RobocodeManager


class K8sManager(RobocodeManager):
    def __init__(self, namespace: str = "robocode", port_number=7654,
                 robocode_image: str = 'gcr.io/stobias-dev/tank-royal-server:0.17.6'):
        super().__init__(port_number=port_number, robocode_image=robocode_image)
        print("loading in cluster config")
        if os.environ.get('KUBECONFIG') == None:
            config.load_incluster_config()
        else:
            config.load_config()
        self.v1_client = client.CoreV1Api()
        self.v1_networking = client.NetworkingV1Api()
        self.conn_pw = 'abc123'
        self.namespace = namespace
        self.port_number = port_number
        self.ip = None
        self.pod_name = f"robocode-training-{self.port_number}-{randint(1, 10000)}"
        self.pod_labels = {"app": "robocode", "instance": self.pod_name}

    # docker run -it --net=host -d --name robocode stobias123/robocode
    def start(self):
        logging.info(f"[Tank Royale] Starting Robocode on port {self.port_number}")
        self.ip = self.create_robocode_game()
        time.sleep(5)
        logging.info(f"[Tank Royale] Started Robocode on port {self.port_number}")

    def create_robocode_game(self):
        self._create_server_pod()
        self._create_service()
        self._create_ingress()
        return self.get_robocode_pod().status.pod_ip

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

    def _create_server_pod(self):
        logging.info(f"[Tank Royale] Creating Robocode Server Pod")
        container = client.V1Container(
            image=self.robocode_image,
            name=self.pod_name,
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
                containers=[container],
                hostname=self.pod_name,
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

    def _create_service(self):
        logging.info(f"[Tank Royale] Creating Robocode Service")
        service = client.V1Service(
            spec=client.V1ServiceSpec(
                selector=self.pod_labels,
                ports=[client.V1ServicePort(
                    port=self.port_number,
                    target_port=self.port_number
                )]
            ),
            metadata=client.V1ObjectMeta(
                name=self.pod_name,
                labels=self.pod_labels,
                owner_references=[client.V1OwnerReference(
                    api_version="v1",
                    kind="Pod",
                    name=self.pod_name,
                    uid=self.get_robocode_pod().metadata.uid,
                    controller=True,
                    block_owner_deletion=True
                )]),
        )
        service = self.v1_client.create_namespaced_service(namespace=self.namespace, body=service)
        return service

    # _create_ingress a python function that creates the ingress defined in k8s/ing.yaml using client.V1Ingress
    def _create_ingress(self):
        logging.info(f"[Tank Royale] Creating Robocode Ingress")
        metadata = client.V1ObjectMeta(
            name=self.pod_name,
            labels=self.pod_labels,
            annotations={
                "nginx.ingress.kubernetes.io/proxy-connect-timeout": "3600",
                "nginx.ingress.kubernetes.io/proxy-read-timeout": "3600",
                "nginx.ingress.kubernetes.io/proxy-send-timeout": "3600",
                "nginx.ingress.kubernetes.io/ssl-redirect": "false",
                "nginx.ingress.kubernetes.io/upstream-keepalive-connections": "1000",
                "nginx.ingress.kubernetes.io/upstream-keepalive-timeout": "3600",
                "nginx.ingress.kubernetes.io/upstream-keepalive": "1000",
                "nginx.ingress.kubernetes.io/rewrite-target": "/",
                "nginx.ingress.kubernetes.io/enable-cors": "true",
                "nginx.ingress.kubernetes.io/configuration-snippet": "proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection \"upgrade\";",
            },
            owner_references=[client.V1OwnerReference(
                api_version="v1",
                kind="Pod",
                name=self.pod_name,
                uid=self.get_robocode_pod().metadata.uid,
                controller=True,
                block_owner_deletion=True
            )]
        )
        ## Create a client v1 ingress rule based on the pod_name
        rule = client.V1IngressRule(
            host=f"{self.pod_name}.svc.bird.co",
            http=client.V1HTTPIngressRuleValue(
                paths=[
                    client.V1HTTPIngressPath(
                        path="/",
                        path_type="Prefix",
                        backend=client.V1IngressBackend(
                                service=client.V1IngressServiceBackend(
                                    name=self.pod_name,
                                    port=client.V1ServiceBackendPort(
                                        number=self.port_number
                                    )
                                )
                            )
                    ),
                ],
            ),
        )

        ## Create a client v1 ingress spec based on the rule
        spec = client.V1IngressSpec(ingress_class_name="ingress-nginx-private", rules=[rule])

        ## Create a client v1 ingress body based on the metadata and spec
        ingress = client.V1Ingress(
            metadata=metadata,
            spec=spec,
        )

        ## Create the ingress using the networking v1 api
        ingress = self.v1_networking.create_namespaced_ingress(
            namespace=self.namespace,
            body=ingress,
        )

        ## Return the ingress
        return ingress
