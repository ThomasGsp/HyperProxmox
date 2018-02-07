#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 Author: Tlams
 Langage: Python
 Minimum version require: 3.4
"""

from core.modules.mod_proxmox import *
from core.modules.mod_database import *
from core.modules.mod_analyst import *
from core.modules.mod_access import *
from core.libs.hcrypt import *
from netaddr import iter_iprange
import threading
import time
import base64


def RunAnalyse(clusters_conf, generalconf, delay=300):
    play = Analyse(clusters_conf, generalconf)


    while True:
        """ Instances types availables: lxc/qemu/all"""
        play.run("all")
        time.sleep(delay)

class Core:

    def __init__(self, generalconf, Lredis):

        self.generalconf = generalconf
        self.Lredis = Lredis

        """ LOAD MONGODB """
        self.mongo = MongoDB(generalconf["mongodb"]["ip"])
        self.mongo.client = self.mongo.connect()

        """ LOAD REDIS """
        self.redis_msg = Lredis

        if self.mongo.client and self.redis_msg.connect():
            self.mongo.db = self.mongo.client.db

            """ Others """
            # value
            self.concurrencydeploy = generalconf["deploy"]["concurrencydeploy"]
            # in seconds
            self.delayrounddeploy = generalconf["deploy"]["delayrounddeploy"]

            """ RUN THE ANALYZER IN DEDICATED THEARD"""
            self.clusters_conf = self.mongo.get_clusters_conf()["value"]

            thc = threading.Thread(name="Update statistics",
                                   target=RunAnalyse,
                                   args=(self.clusters_conf, self.generalconf))
            thc.start()


    """
    #######################
    #  GENERAL FUNCTIONS  #
    #######################
    """
    def is_json(selmyjson):
        try:
            json.loads(myjson)
        except ValueError as e:
            return False
        return True

    def generalsearch(self, collection, id):
        try:
            return self.mongo.generalmongosearch(collection, str(id))
        except:
            return json_decode({"value": "Bad request"})

    def generalquerycacheinfra(self, dest, date, cluster=None, node=None, vmid=None):
        if dest == "instances":
            return self.mongo.get_instance(date, cluster, node, vmid)
        elif dest == "nodes":
            return self.mongo.get_nodes_informations(date, cluster, node)
        elif dest == "clusters":
            return self.mongo.get_clusters_conf(date, cluster)
        else:
            json_decode({"value": "Bad request"})



    """ 
    #######################
    # INSTANCE MANAGEMENT #
    #######################
    """
    def insert_instance(self, node, cluster, count=1, command_id=000000,  instancetype="lxc"):

        """ Find cluster informations from node """
        lastkeyvalid = self.mongo.get_last_datekey()
        node_informations = self.mongo.get_nodes_informations((int(lastkeyvalid["value"])), node, cluster)
        cluster_informations = self.mongo.get_clusters_conf(cluster)["value"]

        proxmox_cluster_url = cluster_informations["url"]
        proxmox_cluster_port = cluster_informations["port"]
        proxmox_cluster_user = pdecrypt(base64.b64decode(cluster_informations["user"]),
                            self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')

        proxmox_cluster_pwd = pdecrypt(base64.b64decode(cluster_informations["password"]),
                                self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')

        proxmox_template = cluster_informations["template"]
        proxmox_storage_disk = cluster_informations["storage_disk"]

        """ LOAD PROXMOX """
        proxmox = Proxmox(node)

        proxmox.get_ticket("{0}:{1}".format(proxmox_cluster_url,
                                                 int(proxmox_cluster_port)),
                           proxmox_cluster_user,
                           proxmox_cluster_pwd)

        returnlistresult = []
        currentcount = 0
        for c in range(0, int(count)):

            if currentcount == self.concurrencydeploy:
                time.sleep(self.delayrounddeploy)
                currentcount = 0

            currentcount = currentcount + 1

            get_info_system = self.mongo.get_system_info()
            """ FIND NEXT INSTANCE ID AVAILABLE  AND INCREMENT IT"""
            next_instance_id = int(get_info_system["instances_number"]+1)

            """ TEST THIS ID """
            

            """ FIND LAST LAST IP  USE  AND INCREMENT IT"""
            if not get_info_system["IP_free"]:
                get_instance_ip = get_info_system["IP_current"]
                next_ip = iter_iprange(get_instance_ip, '172.16.255.250', step=1)
                # Revoir pour un truc plus clean ....
                next(next_ip)
                ip = str(next(next_ip))
            else:
                ip = str(get_info_system["IP_free"][0])
                self.mongo.update_system_delete_ip(ip)

            # insert check duplicate entry
            """ INSTANCE DEFINITION """
            data = {
                'ostemplate': proxmox_template,
                'vmid': next_instance_id,
                'storage': proxmox_storage_disk,
                'cores': 1,
                'cpulimit': 1,
                'cpuunits': 512,
                'arch': "amd64",
                'memory': 256,
                'description': command_id,
                'onboot': 0,
                'swap': 256,
                'ostype': 'debian',
                'net0': 'name=eth0,bridge=vmbr1,ip={0}/16,gw=172.16.1.254'.format(ip),
                'ssh-public-keys': get_info_system["sshpublickey"]
            }

            """ INSTANCE INSERTION """
            result_new = proxmox.create_instance("{0}:{1}".format(proxmox_cluster_url,
                                                     int(proxmox_cluster_port)), node, instancetype,
                                                    data)
            """ Get first digest """
            digest_init = proxmox.get_config("{0}:{1}".format(proxmox_cluster_url,
                                                         int(proxmox_cluster_port)),
                                             node, instancetype, next_instance_id)['value']['data']['digest']


            """ VERIFY THE RESULT BY PROXMOX STATUS REQUEST CODE """
            if result_new['result'] == "OK":
                """ INCREMENT INSTANCE ID IN DATABASE """
                self.mongo.update_system_instance_id(next_instance_id)
                """ INCREMENT INSTANCE IP IN DATABASE """
                self.mongo.update_system_instance_ip(ip)

                """ INSERT THIS NEW SERVER IN DATABASE """
                data["commandid"] = command_id
                data["cluster"] = node_informations["cluster"]
                data["node"] = target
                data["ip"] = ip

                self.mongo.insert_instance(data)
                """ Limit creation DDOS based on digest """
                while digest_init == proxmox.get_config("{0}:{1}".format(proxmox_cluster_url,
                                                    int(proxmox_cluster_port)),
                                                    node, instancetype, next_instance_id)['value']['data']['digest']:
                    time.sleep(5)

            returnlistresult.append(result_new)

        """ SEND MESSAGE IN REDIS """
        self.redis_msg.insert_message(command_id, returnlistresult)

        return

    def delete_instance(self, vmid, instancetype="lxc"):

        try:
            """ Find node/cluster informations from vmid """
            instance_informations = self.mongo.get_instance(vmid)

            """ Find cluster informations from node """
            cluster_informations = self.mongo.get_clusters_conf(instance_informations['cluster'])["value"]

            proxmox_cluster_url = cluster_informations["url"]
            proxmox_cluster_port = cluster_informations["port"]
            proxmox_cluster_user = pdecrypt(base64.b64decode(cluster_informations["user"]),
                                            self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')

            proxmox_cluster_pwd = pdecrypt(base64.b64decode(cluster_informations["password"]),
                                           self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')
            """ LOAD PROXMOX """
            proxmox = Proxmox(instance_informations['node'])
            proxmox.get_ticket("{0}:{1}".format(proxmox_cluster_url,
                                                int(proxmox_cluster_port)),
                               proxmox_cluster_user,
                               proxmox_cluster_pwd)

            result = proxmox.delete_instance("{0}:{1}".format(proxmox_cluster_url,
                                                              int(proxmox_cluster_port)),
                                             instance_informations['node'], instancetype, vmid)

            if result['result'] == "OK":
                self.mongo.delete_instance(vmid)
                self.mongo.update_system_free_ip(instance_informations['ip'])

        except IndexError as ierror:
            result = {
                "result": "ERROR",
                "type": "PROXMOX - VALUES",
                "value": "{0} is not a valid VMID: {1}".format(vmid, ierror)
            }

        return result

    def status_instance(self, vmid, action,  instancetype="lxc"):
        """ Find node/cluster informations from vmid """
        try:
            instance_informations = self.mongo.get_instance(vmid)

            """ Find cluster informations from node """
            cluster_informations = self.mongo.get_clusters_conf(instance_informations['cluster'])["value"]

            proxmox_cluster_url = cluster_informations["url"]
            proxmox_cluster_port = cluster_informations["port"]
            proxmox_cluster_user = pdecrypt(base64.b64decode(cluster_informations["user"]),
                                            self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')

            proxmox_cluster_pwd = pdecrypt(base64.b64decode(cluster_informations["password"]),
                                           self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')
            """ LOAD PROXMOX """
            proxmox = Proxmox(instance_informations['node'])
            proxmox.get_ticket("{0}:{1}".format(proxmox_cluster_url,
                                                     int(proxmox_cluster_port)),
                               proxmox_cluster_user,
                               proxmox_cluster_pwd)

            result = proxmox.status_instance("{0}:{1}".format(proxmox_cluster_url,
                                                              int(proxmox_cluster_port)),
                                             instance_informations['node'],
                                             instancetype,
                                             vmid, action)

        except IndexError as ierror:
            result = {
                "result": "ERROR",
                "type": "PROXMOX - VALUES",
                "value": "{0} is not a valid VMID: {1}".format(vmid, ierror)
            }

        return result

    def info_instance(self, vmid, instancetype="lxc"):
        """ Find node/cluster informations from vmid """
        try:
            instance_informations = self.mongo.get_instance(vmid)

            """ Find cluster informations from node """
            cluster_informations = self.mongo.get_clusters_conf(instance_informations['cluster'])["value"]

            proxmox_cluster_url = cluster_informations["url"]
            proxmox_cluster_port = cluster_informations["port"]
            proxmox_cluster_user = pdecrypt(base64.b64decode(cluster_informations["user"]),
                                            self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')

            proxmox_cluster_pwd = pdecrypt(base64.b64decode(cluster_informations["password"]),
                                           self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')
            """ LOAD PROXMOX """
            proxmox = Proxmox(instance_informations['node'])
            proxmox.get_ticket("{0}:{1}".format(proxmox_cluster_url,
                                                     int(proxmox_cluster_port)),
                               proxmox_cluster_user,
                               proxmox_cluster_pwd)

            result = proxmox.get_config("{0}:{1}".format(proxmox_cluster_url,
                                                              int(proxmox_cluster_port)),
                                             instance_informations['node'],
                                             instancetype,
                                             vmid)

        except IndexError as ierror:
            result = {
                "result": "ERROR",
                "type": "PROXMOX - VALUES",
                "value": "{0} is not a valid VMID: {1}".format(vmid, ierror)
            }

        return result

    def change_instance(self, vmid, data, instancetype="lxc"):
        """ Find node/cluster informations from vmid """
        try:
            instance_informations = self.mongo.get_instance(vmid)

            """ Find cluster informations from node """
            cluster_informations = self.mongo.get_clusters_conf(instance_informations['cluster'])["value"]

            proxmox_cluster_url = cluster_informations["url"]
            proxmox_cluster_port = cluster_informations["port"]
            proxmox_cluster_user = pdecrypt(base64.b64decode(cluster_informations["user"]),
                                            self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')

            proxmox_cluster_pwd = pdecrypt(base64.b64decode(cluster_informations["password"]),
                                           self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')

            """ LOAD PROXMOX """
            proxmox = Proxmox(instance_informations['node'])
            proxmox.get_ticket("{0}:{1}".format(proxmox_cluster_url,
                                                int(proxmox_cluster_port)),
                               proxmox_cluster_user,
                               proxmox_cluster_pwd)

            result = proxmox.resize_instance("{0}:{1}".format(proxmox_cluster_url,
                                                              int(proxmox_cluster_port)),
                                             instance_informations['node'],
                                             instancetype,
                                             vmid, data)

            if result['result'] == "OK":
                self.mongo.update_instance(data, vmid)

        except IndexError as ierror:
            result = {
                "result": "ERROR",
                "type": "PROXMOX - VALUES",
                "value": "{0} is not a valid VMID: {1}".format(vmid, ierror)
            }

        return result

    """ 
    #######################
    # CLUSTERS MANAGEMENT #
    #######################
    """

    def get_cluster(self, cluster=None):
        """ Find cluster informations from node """
        cluster_informations = self.mongo.get_clusters_conf(cluster)["value"]
        return cluster_informations

    def insert_cluster(self, data):
        testdata = valid_cluster_data(data)

        if not testdata:
            if not self.mongo.get_clusters_conf(data["name"])["value"]:
                data["user"] = base64.b64encode(pcrypt(data["user"], self.generalconf["keys"]["key_pvt"])["data"]).decode('utf-8')
                data["password"] = base64.b64encode(pcrypt(data["password"], self.generalconf["keys"]["key_pvt"])["data"]).decode('utf-8')
                new_cluster = self.mongo.insert_new_cluster(data)
            else:
                new_cluster = {
                    "value": "{0}".format("Duplicate entry, please delete the current cluster or update it"),
                    "result": "ERROR",
                    "type": "PROXMOX - VALUES"
                }
        else:
            new_cluster = {
                "value": "{1} {0}".format(testdata, "Invalid or miss paramettrer"),
                "result": "ERROR",
                "type": "PROXMOX - VALUES"
            }

        return new_cluster

    def change_cluster(self, cluster, data):
        cluster_update = self.mongo.update_cluster(cluster, data)
        return cluster_update


    def delete_cluster(self, cluster):
        """ Find cluster informations from node """
        cluster_delete = self.mongo.delete_cluster(cluster)
        return cluster_delete


    """ 
    #######################
    # STORAGES MANAGEMENT #
    #######################
    """

    """ 
    #######################
    #  NODES  MANAGEMENT  #
    #######################
    """



def valid_cluster_data(data):
    key_required = ["name", "url", "port", "user", "password", "template", "storage_disk", "weight", "exclude_nodes"]
    result = []
    for key in key_required:
        if key not in data:
            result.append(key)
    return result
