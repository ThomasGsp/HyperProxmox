from pymongo import MongoClient
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
            conn = self.r = redis.Redis(
                host=self.server, port=self.port, db=self.db, password=self.password,
                charset="utf-8", decode_responses=True)
            self.r.client_list()
        except BaseException as err:
            print("Redis connexion error on {0}:{1} ({2})".format(self.server, self.port, err))
            conn = False
        return conn

    def insert_instance_queue(self,  logtext, expir=3000):
        self.r.set(time.time(), logtext, expir)

    def insert_logs(self,  logtext, expir=86400*4):
        self.r.set(time.time(), logtext, expir)

    def insert_message(self, key, value, expir=86400):
        self.r.set(key, value, expir)

    def get_message(self, key):
        return self.r.get(key)


class MongoDB:
    def __init__(self, server="127.0.0.1", port=27017):
        """
        :param server:
        :param port:
        """
        self.server = server
        self.port = port
        self.collection_system = "system"
        self.collection_instance = "instances"
        self.collection_nodes = "nodes"
        self.collection_clusters = "clusters"
        self.collection_storages = "storages"
        self.collection_datekey = "dates"
        self.port = port
        self.db = None
        self.client = None

    def connect(self):
        try:
            conn = MongoClient(self.server + ':' + str(self.port))
            conn.server_info()
        except BaseException as err:
            print("MongoDB connexion error on {0}:{1} ({2})".format(self.server, self.port, err))
            conn = False
        return conn

    def authenticate(self, user=None, password=None, mechanism='SCRAM-SHA-1'):
        try:
            self.client.db.authenticate(user, password, mechanism)
        except (TypeError, ValueError) as e:
            raise("MongoDB authentification error on {0}:{1} ({2})".format(self.server, self.port, e))


    def generalmongosearch(self, collection, id):
        try:
            result = {
                "result": "OK",
                "value": json.loads(dumps(self.db[collection].find({"_id": id})))
            }
        except BaseException as e:
            result = {
                "result": "ERROR",
                "value": "Invalid request: {0}".format(e)
            }
        return result


    """ CLUSTER """
    def get_clusters_conf(self, cluster=None):
        try:
            if cluster:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(self.db[self.collection_clusters].find_one({"name": cluster})))
                }
            else:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(self.db[self.collection_clusters].find({})))
                }
        except BaseException as e:
            result = {
                "result": "ERROR",
                "value": "Invalid request: {0}".format(e)
            }
        return result

    def insert_new_cluster(self, data):
        try:
            self.db[self.collection_clusters].insert(data)
            result = {
                "result": "OK",
                "value": "{0} is now available".format(data["name"])
            }
        except BaseException as e:
            result = {
                "result": "ERROR",
                "value": "Invalid request: {0}".format(e)
            }
        return result

    def update_cluster(self, cluster, data):
        try:
            self.db[self.collection_clusters].update({"vmid": str(cluster)}, {'$set': data}, upsert=False)
            result = {
                "result": "OK",
                "value": "{0} has been updated".format(data["name"])
            }
        except BaseException as e:
            result = {
                "result": "ERROR",
                "value": "Invalid request: {0}".format(e)
            }
        return result

    def delete_cluster(self, cluster):
        try:
            self.db[self.collection_clusters].remove({"cluster": str(cluster)})
            result = {
                "result": "OK",
                "value": "{0} {1}".format(cluster, "has been deleted")
            }
        except BaseException as e:
            result = {
                "result": "ERROR",
                "value": "Invalid request: {0}".format(e)
            }
        return result

    """ SYSTEM """
    def get_system_info(self):
        return self.db[self.collection_system].find_one({"_id": "0"})

    def update_system_instance_id(self, value):
        self.db[self.collection_system].update({'_id': "0"}, {'$set': {'instances_number': value}})

    def update_system_instance_ip(self, value):
        self.db[self.collection_system].update({'_id': "0"}, {'$set': {'IP_current': value}})

    def update_system_free_ip(self, value):
        self.db[self.collection_system].update({'_id': "0"}, {'$push': {'IP_free': value}}, upsert=False)

    def update_system_delete_ip(self, value):
        self.db[self.collection_system].update({'_id': "0"}, {'$pull': {'IP_free': value}}, upsert=False)



    """ KEY DATE MANAGEMENT"""
    def insert_datekey(self, date, status):
        return self.db[self.collection_datekey].insert({'date': int(date), 'status': status})

    def update_datekey(self, date, status):
        self.db[self.collection_datekey].update({'date': date}, {'$set': {'status': status}}, upsert=False)

    def get_last_datekey(self):
        last_id = self.db[self.collection_datekey].find({'status': 'OK'}).sort("date", -1).limit(1)
        return {"value": int(json.loads(dumps(last_id))[0]['date'])}

    """ NODES MANAGEMENT"""
    def insert_node(self, data):
        try:
            return self.db[self.collection_nodes].insert(data)
        except BaseException as serr:
            raise ("MongoDB error on {0}:{1} ({2})".format(self.server, self.port, serr))

    def get_node(self, date, cluster, node, grata=0):
        try:
            if not cluster:
                result = {
                    "result": "OK",
                    "value": json.loads(
                        dumps(self.db[self.collection_nodes].find(
                            {'$and': [{'date': date, 'grata': str(grata)}]})))
                }
            elif not node:
                result = {
                    "result": "OK",
                    "value": json.loads(
                        dumps(self.db[self.collection_nodes].find(
                        {'$and': [{'date': date, 'cluster': cluster, 'grata': str(grata)}]})))
                }
            else:
                result = {
                    "result": "OK",
                    "value": json.loads(
                        dumps(self.db[self.collection_nodes].find_one(
                            {'$and': [{'date': date, 'cluster': cluster, 'node': node, 'grata': str(grata)}]})))
                }

        except BaseException as serr:
            result = {
                "result": "ERROR",
                "value": "MongoDB error on {0}:{1} ({2})".format(self.server, self.port, serr)
            }
        return result

    """ INSTANCE MANAGEMENT"""
    def insert_instance(self, data):
        try:
            return self.db[self.collection_instance].insert(data)
        except BaseException as serr:
            raise ("MongoDB error on {0}:{1} ({2})".format(self.server, self.port, serr))

    # Revoir la multiplicite des instances/nodes
    def get_instance(self, date, cluster, node, vmid):
        try:
            if not cluster:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(
                        self.db[self.collection_instance].find({"date": int(date)})))
                }
            elif not node:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(
                        self.db[self.collection_instance].find(
                            {'$and': [{"date": int(date), "cluster": cluster}]})))
                }
            elif not vmid:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(
                        self.db[self.collection_instance].find(
                            {'$and': [{"date": int(date), "cluster": cluster, "node": node}]})))
                }
            else:
                result = {
                    "result": "OK",
                    "value": json.loads(dumps(
                        self.db[self.collection_instance].find_one(
                            {'$and': [{"date": int(date), "cluster": cluster, "node": node, "vmid": int(vmid)}]})))
                }

        except BaseException as serr:
            result = {
                "result": "ERROR",
                "value": "MongoDB error on {0}:{1} ({2})".format(self.server, self.port, serr)
            }
        return result
