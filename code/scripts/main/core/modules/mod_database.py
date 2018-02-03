from pymongo import MongoClient
from bson.json_util import dumps
import json
import redis
import time

class Redis_instance_queue:
    def __init__(self, server="127.0.0.1", port=6379, db=3, password=None):
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


class Redis_logger:
    def __init__(self, server="127.0.0.1", port=6379, db=2, password=None):
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

    def insert_logs(self,  logtext, expir=86400*4):
        self.r.set(time.time(), logtext, expir)


class Redis_messages:
    def __init__(self, server="127.0.0.1", port=6379, db=1, password=None):
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
                "value": "{0} {1}".format("Invalid request", e)
            }
        return result

    def insert_new_cluster(self, data):
        try:
            self.db[self.collection_clusters].insert(data)
            result = {
                "result": "OK",
                "value": "{0} {1}".format(data["name"], "is now available")
            }
        except BaseException as e:
            result = {
                "result": "ERROR",
                "value": "{0} {1}".format("Invalid request", e)
            }
        return result

    def update_cluster(self, cluster, data):
        try:
            self.db[self.collection_clusters].update({"vmid": str(cluster)}, {'$set': data}, upsert=False)
            result = {
                "result": "OK",
                "value": "{0} {1}".format(data["name"], "has been updated")
            }
        except BaseException as e:
            result = {
                "result": "ERROR",
                "value": "{0} {1}".format("Invalid request", e)
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
                "value": "{0} {1}".format("Invalid request", e)
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

    """ NODES MANAGEMENT"""
    def insert_node(self, data):
        return self.db[self.collection_nodes].insert(data)

    def get_nodes_informations(self, time, node=None):
        if node:
            return json.loads(dumps(self.db[self.collection_nodes].find_one({'$and': [{'node': node, 'date': time}]})))
        else:
            return json.loads(dumps(self.db[self.collection_nodes].find({'date': time})))

    """ KEY DATE MANAGEMENT"""
    def insert_datekey(self, date, status):
        return self.db[self.collection_datekey].insert({'date': int(date), 'status': status})

    def update_datekey(self, date, status):
        self.db[self.collection_datekey].update({'date': date}, {'$set': {'status': status}}, upsert=False)

    def get_last_datekey(self):
        last_id = self.db[self.collection_datekey].find({'status': 'OK'}).sort("date", -1).limit(1)
        return {"value": int(json.loads(dumps(last_id))[0]['date'])}

    """ INSTANCE MANAGEMENT"""
    def insert_instance(self, data):
        return self.db[self.collection_instance].insert(data)

    def update_instance(self, data, vmid, node=None, cluster=None):
        if node and cluster:
            return self.db[self.collection_instance].update(
                {"vmid": int(vmid), "node": node, "cluster": cluster }, {'$set': data}, upsert=False)
        else:
            return self.db[self.collection_instance].update({"_id": vmid}, {'$set': data}, upsert=False)

    def delete_instance(self, vmid, node=None, cluster=None):
        if node and cluster:
            self.db[self.collection_instance].remove({"vmid": int(vmid), "node": node, "cluster": cluster})
        else:
            self.db[self.collection_instance].remove({"_id": vmid})

    def get_instance(self, vmid, node=None, cluster=None):
        try:
            if node and cluster:
                return json.loads(dumps(
                    self.db[self.collection_instance].find_one(
                        {"vmid": int(vmid), "node": node, "cluster": cluster})))
            else:
                return json.loads(dumps(
                    self.db[self.collection_instance].find_one({"_id": vmid})))
        except BaseException as serr:
            raise ("MongoDB error on {0}:{1} ({2})".format(self.server, self.port, serr))
