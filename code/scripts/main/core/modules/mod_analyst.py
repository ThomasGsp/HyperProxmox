"""
Author: Tlams
Langage: Python
Minimum version require: 3.4

Module function:
The goal of this module is to analyse the differents clusters and node
to allocate news instances.
"""

from core.modules.mod_proxmox import *
from core.modules.mod_database import *
from core.libs.hcrypt import *
from core.libs.locker import *
import time
import operator
import random
import base64


def add_token(tokens_in_slots, slot_distributions):
    num_tokens = sum(tokens_in_slots)
    if not num_tokens:
        #first token can go anywhere
        tokens_in_slots[random.randint(0, 2)] += 1
        return
    expected_tokens = [num_tokens*distr for distr in slot_distributions]
    errors = [expected - actual
              for expected, actual in zip(expected_tokens, tokens_in_slots)]
    most_error = max(enumerate(errors), key=lambda i_e: i_e[1])
    tokens_in_slots[most_error[0]] += 1


def distribution(n, tokens_in_slots, slot_distributions):
    for i in range(n):
        add_token(tokens_in_slots, slot_distributions)
    return tokens_in_slots


class Analyse:
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

    def run(self, instancetype="all"):
        insert_time = time.time()

        """ Create lock file """
        locker = Locker()
        locker.createlock(self.generalconf["hyperproxmox"]["walker_lock"], insert_time)

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

            """ 
            ##############
            #  CLUSTERS  #
            ##############
            """

            """ Get excluded nodes """
            exclude_nodes = cluster["exclude_nodes"]

            """ UPDATE CLUSTER STATUS """
            clusters_status = proxmox.get_clusters("{0}:{1}".format(cluster["url"], int(cluster["port"])))
            clusters_status["date"] = int(insert_time)
            clusters_status["cluster"] = cluster["name"]
            self.mongo.insert_cluster(instance)

            """ UPDATE NODES LIST """
            nodes_list = proxmox.get_nodes("{0}:{1}".format(cluster["url"], int(cluster["port"])))
            if nodes_list["result"] == "OK":
                for value_nodes_list in nodes_list["value"]["data"]:
                    # if value_nodes_list["node"] not in exclude_nodes:
                    """ TOTAL COUNT CPU and RAM allocate """
                    if (instancetype == "all"):
                        types = ["lxc", "qemu"]  # vz...
                        for type in types:
                            list_instances.update(
                                proxmox.get_instance("{0}:{1}".format(cluster["url"], int(cluster["port"])),
                                                     value_nodes_list["node"], type)["value"])
                    else:
                        list_instances = \
                        proxmox.get_instance("{0}:{1}".format(cluster["url"], int(cluster["port"])),
                                             value_nodes_list["node"], instancetype)["value"]

                    totalcpu = 0
                    totalram = 0

                    """ 
                    #############
                    # INSTANCES #
                    #############
                    """
                    for key_list_instances, value_list_instances in list_instances.items():
                        for instances in value_list_instances:
                            """ Update cpu and ram for node """
                            totalcpu = totalcpu + instances["cpus"]
                            totalram = totalram + instances["maxmem"]

                            """ Update instance list """
                            instance["cluster"] = cluster["name"]
                            instance["node"] = value_nodes_list["node"]
                            instance["date"] = int(insert_time)
                            self.mongo.insert_instance(instance)

                    """ 
                    #############
                    #   NODES   #
                    #############
                    """
                    value_nodes_list["totalalloccpu"] = totalcpu
                    value_nodes_list["totalallocram"] = totalram
                    value_nodes_list["vmcount"] = len(list_instances.items())

                    percent_cpu_alloc = (totalcpu / value_nodes_list["maxcpu"]) * 100
                    percent_ram_alloc = (totalram / value_nodes_list["mem"]) * 100

                    """
                    weight of node =
                    (((Percent Alloc CPU x coef) + ( Percent Alloc RAM x coef)) / Total coef ) * Cluster weight
                    """
                    weight = (((percent_cpu_alloc * 2) + (percent_ram_alloc * 4)) / 6) * int(cluster["weight"])

                    value_nodes_list["weight"] = int(weight)
                    value_nodes_list["date"] = int(insert_time)
                    value_nodes_list["cluster"] = cluster["name"]

                    """ Mark the node as an grata or not grata """
                    if value_nodes_list["node"] in exclude_nodes:
                        value_nodes_list["grata"] = 0
                    else:
                        value_nodes_list["grata"] = 1

                    self.mongo.insert_node(value_nodes_list)

                    """ 
                    #############
                    #  STORAGES #
                    #############
                    """
                    storages_list = proxmox.get_storages("{0}:{1}".format(cluster["url"], int(cluster["port"])),
                                                         value_nodes_list["node"])
                    for storage in storages_list:
                        storage["node"] = value_nodes_list["node"]
                        storage["date"] = int(insert_time)
                        storage["cluster"] = cluster["name"]

                        self.mongo.insert_storage(storage)
                        disks_list = proxmox.get_storages("{0}:{1}".format(cluster["url"], int(cluster["port"])),
                                                         value_nodes_list["node"], storage["storage"])

                        for disk in disks_list:
                            disk["storage"] = storage["storage"]
                            disk["node"] = value_nodes_list["node"]
                            disk["date"] = int(insert_time)
                            disk["cluster"] = cluster["name"]
                            self.mongo.insert_disk(disk)

            else:
                print(nodes_list)

        self.mongo.update_datekey(int(insert_time), "OK")

        """ Unlock file """
        locker.unlock(self.generalconf["hyperproxmox"]["walker_lock"])

        return

    def set_attribution(self, count):
        """ RETURN cluster and node"""
        # Search the last valid key
        lastkeyvalid = self.mongo.get_last_datekey()

        # Get nodes weight with good grata !!
        nodes_availables = self.mongo.get_nodes(int(lastkeyvalid["value"]), None, 1)

        if len(nodes_availables) > 1:
            # Select node name with weight
            nodes_values = {}
            for nodes in nodes_availables:
                nodes_values[nodes["_id"]] = nodes["weight"]

            # Sort node by weight
            sorted_nodes = sorted(nodes_values.items(), key=operator.itemgetter(1))

            slot_distributions = []
            sorted_nodes_name = []

            # Divise dict sorted_node to two list [name1, name2] [value1, value2]
            for nodes_sort in sorted_nodes:
                slot_distributions.append(nodes_sort[1])
                sorted_nodes_name.append((nodes_sort[0]))

            # Calcul weight on a range of value  0-1 and convert in percent
            slot_distributions_p = []
            for s in slot_distributions:
                slot_distributions_p.append(100-(s/sum(slot_distributions)*100)/100)

            # Generate default list
            tokens_in_slots = [0] * len(nodes_availables)

            # use distribution algorithm to allocate
            distrib_final = distribution(int(count), tokens_in_slots, slot_distributions_p)

            # Regenerate final dict !!
            final = {k: int(v) for k, v in zip(sorted_nodes_name, distrib_final)}

        else:
            final = {nodes_availables[0]['_id']: count}

        return final
