from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
import json
import redis
import time

class Redis_wrapper:
    def __init__(self, server="127.0.0.1", port=6379, db=0, password=None):
        # DB =
        # messages: 0
        # logs: 1
        # queue : 2
        # cache : 3

        self.server = server
        self.port = port
        self.r = None
        self.db = db
        self.password = password

    def connect(self):
        try:
            conn = self.r = redis.StrictRedis(
                host=self.server, port=self.port, db=self.db, password=self.password,
                charset="utf-8", decode_responses=True)
            self.r.client_list()
            return conn
        except BaseException as err:
            print("Redis connexion error on {0}:{1} ({2})".format(self.server, self.port, err))

    def insert_instances_queue(self,  logtext, expir=3000):
        self.r.set(time.time(), logtext, expir)

    def insert_logs(self,  logtext, expir=86400*4):
        self.r.set(time.time(), logtext, expir)

    def insert_message(self, key, value, expir=86400):
        self.r.set(key, value, expir)

    def get_message(self, key):
        try:
            result = json.loads(dumps(self.r.get(key)))
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "Redis - Request on get_message",
                "value": "Invalid request: {0}".format(e)
            }
        return result

class MongoDB:
    def __init__(self, server="127.0.0.1", port=27017):
        """
        :param server:
        :param port:
        """
        self.server = server
        self.port = port
        self.collection_system = "system"
        self.collection_instances = "instances"
        self.collection_nodes = "nodes"
        self.collection_clusters = "clusters"
        self.collection_clusters_conf = "clusters_conf"
        self.collection_storages = "storages"
        self.collection_disks = "disks"
        self.collection_datekey = "dates"
        self.port = port
        self.db = None
        self.client = None

    def connect(self):
        try:
            conn = MongoClient(self.server + ':' + str(self.port))
            conn.server_info()
            return conn
        except BaseException as err:
            print("MongoDB connexion error on {0}:{1} ({2})".format(self.server, self.port, err))

    def authenticate(self, user=None, password=None, mechanism='SCRAM-SHA-1'):
        try:
            self.client.db.authenticate(user, password, mechanism)
        except (TypeError, ValueError) as e:
            print("MongoDB authentification error on {0}:{1} ({2})".format(self.server, self.port, e))

    def generalmongosearch(self, collection, id):
        try:
            result = {
                "result": "OK",
                "value": json.loads(dumps(self.db[collection].find_one({"_id": ObjectId(id)})))
            }
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "MongoDB - Request on generalmongosearch",
                "value": "Invalid request: {0}".format(e)
            }
        return result

    """ CLUSTER """
    def get_clusters(self, date, cluster):
        try:
            if not cluster:
                result = {
                    "result": "OK",
                    "value": json.loads(
                        dumps(self.db[self.collection_clusters].find({'date': int(date)})))
                }
            else:
                result = {
                    "result": "OK",
                    "value": json.loads(
                        dumps(self.db[self.collection_clusters].find(
                            {'$and': [{'date': int(date), 'cluster': cluster}]})))
                }

        except BaseException as serr:
            result = {
                "result": "ERROR",
                "type": "MongoDB - Request on get_clusters",
                "value": "MongoDB error on {0}:{1} ({2})".format(self.server, self.port, serr)
            }
        return result

    def insert_clusters(self, data):
        try:
            result = {
                "result": "OK",
                "value": json.loads(dumps(self.db[self.collection_clusters].insert(data)))
            }

        except BaseException as serr:
            result = {
                "result": "ERROR",
                "type": "MongoDB - Request on insert_clusters",
                "value": "MongoDB error on {0}:{1} ({2})".format(self.server, self.port, serr)
            }
        return result

    def get_clusters_conf(self, cluster=None):
        try:
            if cluster:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(self.db[self.collection_clusters_conf].find_one({"name": cluster})))
                }
            else:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(self.db[self.collection_clusters_conf].find({})))
                }
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "MongoDB - Request on get_cluster_conf",
                "value": "Invalid request: {0}".format(e)
            }
        return result

    def insert_clusters_conf(self, data):
        try:
            self.db[self.collection_clusters_conf].insert(data)
            result = {
                "result": "OK",
                "value": "{0} is now available".format(data["name"])
            }
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "MongoDB - Request on insert_cluster_conf",
                "value": "Invalid request: {0}".format(e)
            }
        return result

    def update_clusters_conf(self, cluster, data):
        try:
            self.db[self.collection_clusters_conf].update({"vmid": str(cluster)}, {'$set': data}, upsert=False)
            result = {
                "result": "OK",
                "value": "{0} has been updated".format(data["name"])
            }
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "MongoDB - Request on update_cluster_conf",
                "value": "Invalid request: {0}".format(e)
            }
        return result

    def delete_clusters_conf(self, cluster):
        try:
            self.db[self.collection_clusters_conf].remove({"cluster": str(cluster)})
            result = {
                "result": "OK",
                "value": "{0} has been deleted".format(cluster)
            }
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "MongoDB - Request on delete_cluster_conf",
                "value": "Invalid request: {0}".format(e)
            }
        return result

    """ SYSTEM """
    def get_system_info(self):
        return self.db[self.collection_system].find_one({"_id": "0"})

    def update_system_instances_id(self, value):
        self.db[self.collection_system].update({'_id': "0"}, {'$set': {'instances_number': value}})

    def update_system_instances_ip(self, value):
        self.db[self.collection_system].update({'_id': "0"}, {'$set': {'IP_current': value}})

    def update_system_free_ip(self, value):
        self.db[self.collection_system].update({'_id': "0"}, {'$push': {'IP_free': value}}, upsert=False)

    def update_system_delete_ip(self, value):
        self.db[self.collection_system].update({'_id': "0"}, {'$pull': {'IP_free': value}}, upsert=False)



    """ KEY DATE MANAGEMENT"""
    def insert_datekey(self, date, status):
        return self.db[self.collection_datekey].insert({'date': int(date), 'status': status})

    def update_datekey(self, date, status):
        self.db[self.collection_datekey].update({'date': int(date)}, {'$set': {'status': status}}, upsert=False)

    def get_last_datekey(self):
        last_id = self.db[self.collection_datekey].find({'status': 'OK'}, {"date": 1, "_id": 0}).sort("date", -1)
        return {"value": int(json.loads(dumps(last_id))[0]['date'])}

    def get_all_datekey(self):
        keylist = self.db[self.collection_datekey].find({'status': 'OK'},
                                                        {"date": 1, "_id": 0}).sort("date", -1)
        return {"value": json.loads(dumps(keylist))}

    """ NODES MANAGEMENT"""
    def insert_nodes(self, data):
        try:
            result = {
                "result": "OK",
                "value": self.db[self.collection_nodes].insert(data)
            }
        except BaseException as serr:
            result = {
                "result": "ERROR",
                "type": "MongoDB - Request on insert_instances",
                "value": "MongoDB error on {0}:{1} ({2})".format(self.server, self.port, serr)
            }
        return result

    def get_nodes(self, date, cluster, node, grata=0):
        try:
            if not cluster:
                result = {
                    "result": "OK",
                    "value": json.loads(
                        dumps(self.db[self.collection_nodes].find(
                            {'date': int(date)})))
                }

            elif not node:
                result = {
                    "result": "OK",
                    "value": json.loads(
                        dumps(self.db[self.collection_nodes].find(
                        {'$and': [{'date': int(date), 'cluster': cluster}]})))
                }
            else:
                result = {
                    "result": "OK",
                    "value": json.loads(
                        dumps(self.db[self.collection_nodes].find(
                            {'$and': [{'date': int(date), 'cluster': cluster, 'node': node}]})))
                }

        except BaseException as serr:
            result = {
                "result": "ERROR",
                "type": "MongoDB - Request on get_nodes",
                "value": "MongoDB error on {0}:{1} ({2})".format(self.server, self.port, serr)
            }
        return result

    """ INSTANCE MANAGEMENT"""
    def insert_instances(self, data):
        try:
            result = {
                "result": "OK",
                "value": self.db[self.collection_instances].insert(data)
            }
        except BaseException as serr:
            result = {
                "result": "ERROR",
                "type": "MongoDB - Request on insert_instances",
                "value": "MongoDB error on {0}:{1} ({2})".format(self.server, self.port, serr)
            }
        return result

    def get_instances(self, date, cluster, node, vmid):
        try:
            if not cluster:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(
                        self.db[self.collection_instances].find({"date": int(date)})))
                }
            elif not node:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(
                        self.db[self.collection_instances].find(
                            {'$and': [{"date": int(date), "cluster": cluster}]})))
                }
            elif not vmid:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(
                        self.db[self.collection_instances].find(
                            {'$and': [{"date": int(date), "cluster": cluster, "node": node}]})))
                }
            else:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(
                        self.db[self.collection_instances].find(
                            {'$and': [{"date": int(date), "cluster": cluster, "node": node, "vmid": int(vmid)}]})))
                }

        except BaseException as serr:
            result = {
                "result": "ERROR",
                "type": "MongoDB - Request on get_instances",
                "value": "MongoDB error on {0}:{1} ({2})".format(self.server, self.port, serr)
            }
        return result


    """ STORAGE MANAGEMENT"""
    def insert_storages(self, data):
        try:
            result = {
                "result": "OK",
                "value": self.db[self.collection_storages].insert(data)
            }
        except BaseException as serr:
            result = {
                "result": "ERROR",
                "type": "MongoDB - Request on insert_storages",
                "value": "MongoDB error on {0}:{1} ({2})".format(self.server, self.port, serr)
            }
        return result

    def get_storages(self, date, cluster, node):
        try:
            if not cluster:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(
                        self.db[self.collection_storages].find({"date": int(date)})))
                }
            elif not node:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(
                        self.db[self.collection_storages].find(
                            {'$and': [{"date": int(date), "cluster": cluster}]})))
                }
            else:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(
                        self.db[self.collection_storages].find(
                            {'$and': [{"date": int(date), "cluster": cluster, "node": node}]})))
                }
        except BaseException as serr:
            result = {
                "result": "ERROR",
                "type": "MongoDB - Request on get_storages",
                "value": "MongoDB error on {0}:{1} ({2})".format(self.server, self.port, serr)
            }
        return result



    """ DISKS MANAGEMENT"""
    def insert_disks(self, data):
        try:
            result = {
                "result": "OK",
                "value": self.db[self.collection_disks].insert(data)
            }
        except BaseException as serr:
            result = {
                "result": "ERROR",
                "type": "MongoDB - Request on get_storages",
                "value": "MongoDB error on {0}:{1} ({2})".format(self.server, self.port, serr)
            }
        return result

    def get_disks(self, date, cluster, node, vmid):
        try:
            if not cluster:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(
                        self.db[self.collection_disks].find({"date": int(date)})))
                }
            elif not node:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(
                        self.db[self.collection_disks].find(
                            {'$and': [{"date": int(date), "cluster": cluster}]})))
                }
            elif not vmid:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(
                        self.db[self.collection_disks].find(
                            {'$and': [{"date": int(date), "cluster": cluster, "node": node}]})))
                }
            else:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(
                        self.db[self.collection_disks].find(
                            {'$and': [{"date": int(date), "cluster": cluster, "node": node, "vmid": str(vmid)}]})))
                }

        except BaseException as serr:
            result = {
                "result": "ERROR",
                "type": "MongoDB - Request on get_disks",
                "value": "MongoDB error on {0}:{1} ({2})".format(self.server, self.port, serr)
            }
        return result