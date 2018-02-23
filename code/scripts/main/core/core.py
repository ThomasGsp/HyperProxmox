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
import hashlib


def RunAnalyse(clusters_conf, generalconf, delay=300):
    play = Analyse(clusters_conf, generalconf)


    while True:
        """ Instances types availables: lxc/qemu/all"""
        play.run("all")
        time.sleep(int(delay))

class Core:

    # def __init__(self, generalconf, Lredis):
    def __init__(self, generalconf):

        self.generalconf = generalconf

        """ LOAD MONGODB """
        self.mongo = MongoDB(generalconf["mongodb"]["ip"])
        self.mongo.client = self.mongo.connect()

        """ LOAD REDIS """
        self.redis_msg = Redis_wrapper(generalconf["redis"]["ip"],
                                       generalconf["redis"]["port"], 0)

        self.redis_cache = Redis_wrapper(generalconf["redis"]["ip"],
                                       generalconf["redis"]["port"], 3)

        self.redis_msg.connect()
        self.redis_cache.connect()

        if self.mongo.client and self.redis_msg.connect() and self.redis_cache.connect():
            self.mongo.db = self.mongo.client.db

            """ Others """
            # value
            self.concurrencydeploy = generalconf["deploy"]["concurrencydeploy"]
            # in seconds
            self.delayrounddeploy = generalconf["deploy"]["delayrounddeploy"]

            """ RUN THE ANALYZER IN DEDICATED THEARD"""
            self.clusters_conf = self.mongo.get_clusters_conf()["value"]

            """ Clean previous lockers """
            locker = Locker()
            locker.unlock(generalconf["analyst"]["walker_lock"], "startup")

            thc = threading.Thread(name="Update statistics",
                                   target=RunAnalyse,
                                   args=(self.clusters_conf, self.generalconf,
                                         generalconf["analyst"]["walker"]))
            thc.start()
        else:
            exit(1)


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

    def getkey(self, keytype):
        if keytype == "all":
            return self.mongo.get_all_datekey()
        elif keytype == "last":
            return self.mongo.get_last_datekey()



    def generalquerycacheinfra(self, dest, date, cluster=None, node=None, vmid=None):

        """ Test Redis Cache """
        hash_object = hashlib.md5("{0}-{1}-{2}-{3}-{4}".format(dest, date, cluster, node, vmid).encode('utf-8'))
        hash_hex = hash_object.hexdigest()

        cache = self.redis_cache.get_message(hash_hex)

        if cache is None or self.generalconf["logger"]["debug"] == True:
            if dest == "instances":
                resultmbrequest = self.mongo.get_instances(date, cluster, node, vmid)
            elif dest == "nodes":
                resultmbrequest = self.mongo.get_nodes(date, cluster, node)
            elif dest == "disks":
                resultmbrequest = self.mongo.get_disks(date, cluster, node, vmid)
            elif dest == "storages":
                resultmbrequest = self.mongo.get_storages(date, cluster, node)
            elif dest == "clusters":
                resultmbrequest = self.mongo.get_clusters(date, cluster)
            else:
                resultmbrequest = json_decode({"value": "Bad request"})

            self.redis_cache.insert_message(hash_hex, resultmbrequest, 3600)
            return resultmbrequest
        else:

            return json.loads(cache.replace("'", "\"").replace("None", "\"\""))


    """ 
    #######################
    # INSTANCE MANAGEMENT #
    #######################
    """
    def insert_instances(self, node, cluster, count=1, command_id=000000,  instancetype="lxc"):

        """ Find cluster informations from node """
        lastkeyvalid = self.mongo.get_last_datekey()
        nodes_informations = self.mongo.get_nodes_informations((int(lastkeyvalid["value"])), node, cluster)
        clusters_informations = self.mongo.get_clusters_conf(cluster)["value"]

        proxmox_clusters_url = clusters_informations["url"]
        proxmox_clusters_port = clusters_informations["port"]
        proxmox_clusters_user = pdecrypt(base64.b64decode(clusters_informations["user"]),
                            self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')

        proxmox_clusters_pwd = pdecrypt(base64.b64decode(clusters_informations["password"]),
                                self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')

        proxmox_template = clusters_informations["template"]
        proxmox_storages_disk = clusters_informations["storages_disk"]

        """ LOAD PROXMOX """
        proxmox = Proxmox(node)

        proxmox.get_ticket("{0}:{1}".format(proxmox_clusters_url,
                                                 int(proxmox_clusters_port)),
                           proxmox_clusters_user,
                           proxmox_clusters_pwd)

        returnlistresult = []
        currentcount = 0
        for c in range(0, int(count)):

            if currentcount == self.concurrencydeploy:
                time.sleep(self.delayrounddeploy)
                currentcount = 0

            currentcount = currentcount + 1

            get_info_system = self.mongo.get_system_info()
            """ FIND NEXT INSTANCE ID AVAILABLE  AND INCREMENT IT"""
            next_instances_id = int(get_info_system["instances_number"]+1)

            """ TEST THIS ID """
            

            """ FIND LAST LAST IP  USE  AND INCREMENT IT"""
            if not get_info_system["IP_free"]:
                get_instances_ip = get_info_system["IP_current"]
                next_ip = iter_iprange(get_instances_ip, '172.16.255.250', step=1)
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
                'vmid': next_instances_id,
                'storage': proxmox_storages_disk,
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
            result_new = proxmox.create_instances("{0}:{1}".format(proxmox_clusters_url,
                                                     int(proxmox_clusters_port)), node, instancetype,
                                                    data)
            """ Get first digest """
            digest_init = proxmox.get_config("{0}:{1}".format(proxmox_clusters_url,
                                                         int(proxmox_clusters_port)),
                                             node, instancetype, next_instances_id)['value']['data']['digest']


            """ VERIFY THE RESULT BY PROXMOX STATUS REQUEST CODE """
            if result_new['result'] == "OK":
                """ INCREMENT INSTANCE ID IN DATABASE """
                self.mongo.update_system_instances_id(next_instances_id)
                """ INCREMENT INSTANCE IP IN DATABASE """
                self.mongo.update_system_instances_ip(ip)

                """ INSERT THIS NEW SERVER IN DATABASE """
                data["commandid"] = command_id
                data["cluster"] = nodes_informations["cluster"]
                data["node"] = target
                data["ip"] = ip
                data["date"] = lastkeyvalid["value"]

                self.mongo.insert_instances(data)
                """ Limit creation DDOS based on digest """
                while digest_init == proxmox.get_config("{0}:{1}".format(proxmox_clusters_url,
                                                    int(proxmox_clusters_port)),
                                                    node, instancetype, next_instances_id)['value']['data']['digest']:
                    time.sleep(5)

            returnlistresult.append(result_new)

        """ SEND MESSAGE IN REDIS """
        self.redis_msg.insert_message(command_id, returnlistresult)

        return

    def delete_instances(self, vmid, instancetype="lxc"):

        try:
            """ Find node/cluster informations from vmid """
            instances_informations = self.mongo.get_instances(vmid)

            """ Find cluster informations from node """
            clusters_informations = self.mongo.get_clusters_conf(instances_informations['cluster'])["value"]

            proxmox_clusters_url = clusters_informations["url"]
            proxmox_clusters_port = clusters_informations["port"]
            proxmox_clusters_user = pdecrypt(base64.b64decode(clusters_informations["user"]),
                                            self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')

            proxmox_clusters_pwd = pdecrypt(base64.b64decode(clusters_informations["password"]),
                                           self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')
            """ LOAD PROXMOX """
            proxmox = Proxmox(instances_informations['node'])
            proxmox.get_ticket("{0}:{1}".format(proxmox_clusters_url,
                                                int(proxmox_clusters_port)),
                               proxmox_clusters_user,
                               proxmox_clusters_pwd)

            result = proxmox.delete_instances("{0}:{1}".format(proxmox_clusters_url,
                                                              int(proxmox_clusters_port)),
                                             instances_informations['node'], instancetype, vmid)

            if result['result'] == "OK":
                self.mongo.delete_instances(vmid)
                self.mongo.update_system_free_ip(instances_informations['ip'])

        except IndexError as ierror:
            result = {
                "result": "ERROR",
                "type": "PROXMOX - VALUES",
                "value": "{0} is not a valid VMID: {1}".format(vmid, ierror)
            }

        return result

    def status_instances(self, id, action):
        """ Find node/cluster informations from vmid """
        try:
            instances_informations = self.mongo.generalmongosearch("instances", id)["value"]

            """ Find cluster informations from node """
            clusters_informations = self.mongo.get_clusters_conf(instances_informations['cluster'])["value"]


            proxmox_clusters_url = clusters_informations["url"]
            proxmox_clusters_port = clusters_informations["port"]
            proxmox_clusters_user = pdecrypt(base64.b64decode(clusters_informations["user"]),
                                            self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')

            proxmox_clusters_pwd = pdecrypt(base64.b64decode(clusters_informations["password"]),
                                           self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')
            """ LOAD PROXMOX """
            proxmox = Proxmox(instances_informations['node'])
            proxmox.get_ticket("{0}:{1}".format(proxmox_clusters_url,
                                                     int(proxmox_clusters_port)),
                               proxmox_clusters_user,
                               proxmox_clusters_pwd)

            result = proxmox.status_instances("{0}:{1}".format(proxmox_clusters_url,
                                                              int(proxmox_clusters_port)),
                                             instances_informations['node'],
                                              instances_informations['type'],
                                              instances_informations['vmid'], action)

        except IndexError as ierror:
            result = {
                "result": "ERROR",
                "type": "PROXMOX - VALUES",
                "value": "{0} is not a valid VMID: {1}".format(vmid, ierror)
            }

        return result

    def info_instances(self, vmid, instancetype="lxc"):
        """ Find node/cluster informations from vmid """
        try:
            instances_informations = self.mongo.get_instances(vmid)

            """ Find cluster informations from node """
            clusters_informations = self.mongo.get_clusters_conf(instances_informations['cluster'])["value"]

            proxmox_clusters_url = clusters_informations["url"]
            proxmox_clusters_port = clusters_informations["port"]
            proxmox_clusters_user = pdecrypt(base64.b64decode(clusters_informations["user"]),
                                            self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')

            proxmox_clusters_pwd = pdecrypt(base64.b64decode(clusters_informations["password"]),
                                           self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')
            """ LOAD PROXMOX """
            proxmox = Proxmox(instances_informations['node'])
            proxmox.get_ticket("{0}:{1}".format(proxmox_clusters_url,
                                                     int(proxmox_clusters_port)),
                               proxmox_clusters_user,
                               proxmox_clusters_pwd)

            result = proxmox.get_config("{0}:{1}".format(proxmox_clusters_url,
                                                              int(proxmox_clusters_port)),
                                             instances_informations['node'],
                                             instancetype,
                                             vmid)

        except IndexError as ierror:
            result = {
                "result": "ERROR",
                "type": "PROXMOX - VALUES",
                "value": "{0} is not a valid VMID: {1}".format(vmid, ierror)
            }

        return result

    def change_instances(self, vmid, data, instancetype="lxc"):
        """ Find node/cluster informations from vmid """
        try:
            instances_informations = self.mongo.get_instances(vmid)

            """ Find cluster informations from node """
            clusters_informations = self.mongo.get_clusters_conf(instances_informations['cluster'])["value"]

            proxmox_clusters_url = clusters_informations["url"]
            proxmox_clusters_port = clusters_informations["port"]
            proxmox_clusters_user = pdecrypt(base64.b64decode(clusters_informations["user"]),
                                            self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')

            proxmox_clusters_pwd = pdecrypt(base64.b64decode(clusters_informations["password"]),
                                           self.generalconf["keys"]["key_pvt"])["data"].decode('utf-8')

            """ LOAD PROXMOX """
            proxmox = Proxmox(instances_informations['node'])
            proxmox.get_ticket("{0}:{1}".format(proxmox_clusters_url,
                                                int(proxmox_clusters_port)),
                               proxmox_clusters_user,
                               proxmox_clusters_pwd)

            result = proxmox.resize_instances("{0}:{1}".format(proxmox_clusters_url,
                                                              int(proxmox_clusters_port)),
                                             instances_informations['node'],
                                             instancetype,
                                             vmid, data)

            if result['result'] == "OK":
                self.mongo.update_instances(data, vmid)

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

    def get_clusters_conf(self, cluster=None):
        ## DELETE USER/PW DATA
        """ Test Redis Cache """
        hash_object = hashlib.md5("{0}-{1}".format("administration", cluster).encode('utf-8'))
        hash_hex = hash_object.hexdigest()

        cache = self.redis_cache.get_message(hash_hex)

        if cache is None or self.generalconf["logger"]["debug"] == True:
            clusters_informations = self.mongo.get_clusters_conf(cluster)
            self.redis_cache.insert_message(hash_hex, clusters_informations, 500)
            return clusters_informations
        else:
            return json.loads(cache.replace("'", "\""))


    def insert_clusters_conf(self, data):
        testdata = valid_clusters_data(data)

        if not testdata:
            if not self.mongo.get_clusters_conf(data["name"])["value"]:
                data["user"] = base64.b64encode(pcrypt(data["user"], self.generalconf["keys"]["key_pvt"])["data"]).decode('utf-8')
                data["password"] = base64.b64encode(pcrypt(data["password"], self.generalconf["keys"]["key_pvt"])["data"]).decode('utf-8')
                new_cluster = self.mongo.insert_clusters_conf(data)
            else:
                new_cluster = {
                    "value": "{0}".format("Duplicate entry, please delete the current cluster or update it"),
                    "result": "ERROR",
                    "type": "PROXMOX - VALUES"
                }
        else:
            new_cluster = {
                "value": "{1} {0}".format(testdata, "Invalid or miss parametrer"),
                "result": "ERROR",
                "type": "PROXMOX - VALUES"
            }

        return new_cluster

    def change_clusters_conf(self, cluster, data):
        clusters_update = self.mongo.update_clusters_conf(cluster, data)
        return clusters_update


    def delete_clusters_conf(self, cluster):
        """ Find cluster informations from node """
        clusters_delete = self.mongo.delete_clusters_conf(cluster)
        return clusters_delete


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



def valid_clusters_data(data):
    key_required = ["name", "url", "port", "user", "password", "template", "storage_disk", "weight", "exclude_nodes", "groups"]
    result = []
    for key in key_required:
        if key not in data:
            result.append(key)
    return result
