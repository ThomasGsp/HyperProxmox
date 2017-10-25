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
import time
import operator
import random
import bson
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

    def run(self):
        insert_time = time.time()

        self.mongo.insert_datekey(insert_time, 'running')

        for cluster in self.clusters_conf:
            """ Decode data """

            user = pdecrypt(base64.b64decode(cluster["user"]), self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')
            password = pdecrypt(base64.b64decode(cluster["password"]), self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')



            """ AUTH """
            proxmox = Proxmox("Analyse")
            proxmox.get_ticket("{0}:{1}".format(cluster["url"],
                                                int(cluster["port"])),
                               pdecrypt(user, self.generalconf["keys"]["key_pvt"]),
                               pdecrypt(password, self.generalconf["keys"]["key_pvt"]))

            """ Get excluded nodes """
            exclude_nodes = cluster["exclude_nodes"]

            """ UPDATE NODES LIST """
            nodes_list = proxmox.get_nodes("{0}:{1}".format(cluster["url"], int(cluster["port"])))["value"]

            for value_nodes_list in nodes_list["data"]:
                if value_nodes_list["node"] not in exclude_nodes:
                    """ TOTAL COUNT CPU and RAM allocate"""
                    list_instances = proxmox.get_instance("{0}:{1}".format(cluster["url"], int(cluster["port"])),
                                                          value_nodes_list["node"], "lxc")["value"]

                    totalcpu = 0
                    totalram = 0
                    for key_list_instances, value_list_instances in list_instances.items():
                        for instances in value_list_instances:
                            totalcpu = totalcpu + instances["cpus"]
                            totalram = totalram + instances["maxmem"]

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

                    self.mongo.insert_node(value_nodes_list)

        self.mongo.update_datekey(int(insert_time), "OK")

        return

    def set_attribution(self, count):
        """ RETURN cluster and node"""
        # Search the last valid key
        lastkeyvalid = self.mongo.get_last_datekey()

        # Get nodes weight
        nodes_availables = self.mongo.get_nodes_informations(int(lastkeyvalid["value"]))

        if len(nodes_availables) > 1:
            # Select node name with weight
            nodes_values = {}
            for nodes in nodes_availables:
                nodes_values[nodes["node"]] = nodes["weight"]

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
            final = {nodes_availables[0]['node']: count}

        return final
