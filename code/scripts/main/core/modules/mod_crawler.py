"""
Author: Tlams
Langage: Python
Minimum version require: 3.4

Module function:
Crawl all node to update the database statistics
"""

from core.modules.mod_proxmox import *
from core.modules.mod_database import *
from core.libs.hcrypt import *
import time
import base64


class Crawler:
    def __init__(self, clusters_conf, generalconf):
        """
        :param clusters_conf: Proxmox configurations
        :param generalconf : General configuration
        """
        self.generalconf = generalconf
        self.clusters_conf = clusters_conf

        """ LOAD MONGODB """
        self.mongo = MongoDB(generalconf["mongodb"]["ip"])
        self.mongo.client = self.mongo.connect()
        self.mongo.db = self.mongo.client.db

    def run(self, instancetype="lxc"):
        insert_time = time.time()

        self.mongo.insert_datekey(insert_time, 'running')

        for cluster in self.clusters_conf:
            """ Decode data """

            proxmox_cluster_user = pdecrypt(base64.b64decode(cluster["user"]),
                            self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')

            proxmox_cluster_pwd = pdecrypt(base64.b64decode(cluster["password"]),
                                self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')

            """ AUTH """
            proxmox = Proxmox("Analyse")
            proxmox.get_ticket("{0}:{1}".format(cluster["url"], int(cluster["port"])), proxmox_cluster_user, proxmox_cluster_pwd)

            """ UPDATE NODES LIST """
            nodes_list = proxmox.get_nodes("{0}:{1}".format(cluster["url"], int(cluster["port"])))
            if nodes_list["result"] == "OK":
                for value_nodes_list in nodes_list["value"]["data"]:
                    """ TOTAL COUNT CPU and RAM allocate"""
                    list_instances = proxmox.get_instance("{0}:{1}".format(cluster["url"], int(cluster["port"])),
                                                          value_nodes_list["node"], instancetype)["value"]

                    for key_list_instances, value_list_instances in list_instances.items():
                        for instance in value_list_instances:
                            instance["cluster"] = cluster["name"]
                            instance["node"] = value_nodes_list["node"]
                            # Test si l'instance existe
                            if not self.mongo.get_instance(instance["vmid"], instance["node"], instance["cluster"]):
                                # si non existante, alors il s'agit d'une instance manuelle
                                instance["commandid"] = "000000"
                                self.mongo.insert_instance(instance)
                            # Si elle existe déjà, on l'update:
                            else:
                                self.mongo.update_instance(instance, instance["vmid"], instance["node"], instance["cluster"])
        return