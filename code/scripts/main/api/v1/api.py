#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import web
from core.core import *
from core.modules.mod_analyst import *
import json
import time
import random
import ast

""" CLASS MONGO CACHE """
class Purge:
    def POST(self):
        try:
            result = core.managedata(json.loads(web.data().decode('utf-8')))
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "Invalid request: {0}".format(e)
            }
        return json.dumps(result)

class General_Search:
    def GET(self, query, id):
        try:
            result = core.generalsearch(query, id)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "Invalid request: {0}".format(e)
            }
        return json.dumps(result)

class QueryCache_Infra:
    def GET(self, dest, date, cluster=None, node=None, vmid=None):
        try:
            result = core.generalquerycacheinfra(dest, date, cluster, node, vmid)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "Invalid request: {0}".format(e)
            }

        return json.dumps(result)

class QueryDates:
    def GET(self, keytype):
        try:
            result = core.getkey(keytype)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "Invalid request: {0}".format(e)
            }
        return json.dumps(result)


""" CLASS DIRECT """
class Cluster:
    def GET(self, cluster=None):
        try:
            if cluster:
                result = core.get_clusters_conf(cluster)
            else:
                result = core.get_clusters_conf()
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "Invalid request: {0}".format(e)
            }

        ## Revoir pour un truc plus clean
        keyv = 0
        for cluster in result["value"]:
            for key in cluster:
                if key == "password" or key == "user":
                    result["value"][keyv][key] = "Information not available"
            keyv += 1

        return json.dumps(result)

    def POST(self, cluster=None):
        try:
            data = json.loads(web.data().decode('utf-8'))
            """ Overwrite name """
            if cluster:
                data["name"] = cluster
            result = core.insert_clusters_conf(data)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "Invalid insert request: {0}".format(e)
            }
        return result

    def PUT(self, cluster):
        try:
            data = json.loads(web.data().decode('utf-8'))
            result = core.change_clusters_conf(cluster, data)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "Invalid update request: {0}".format(e)
            }
        return result

    def DELETE(self, cluster):
        try:
            result = core.delete_clusters_conf(cluster)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "Invalid delete request: {0}".format(e)
            }
        return result


class Instance:
    def GET(self, id, action=None):
        try:
            if action:
                """ GET INSTANCE STATUS """
                result = core.status_instances(id, action)
            else:
                """ GET INSTANCE INFORMATION """
                result = core.info_instances(id)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "Invalid request: {0}".format(e)
            }
        return json.dumps(result)

    def POST(self, vmid=None, status=None):
        try:
            if vmid:
                """ GET INSTANCE INFORMATION """
                result = core.status_instances(vmid, status)
            else:
                """ CREATE NEWS INSTANCES"""
                count = json.loads(web.data().decode('utf-8'))["count"]

                """ LOAD CLUSTER CONFIGURATIONS """
                select = Analyse(core.clusters_conf, generalconf)
                sorted_nodes = dict(select.set_attribution(count))

                """ START ALL Thread """
                for nodeid, count in sorted_nodes.items():
                    """ GENERATE UNIQ COMMAND ID """
                    randtext = ''.join(random.choice('AZERTYUIOPQSDFGHJKLMWXCVBN') for i in range(8))
                    command_id = "-- Please, do not change or delete this ID -- \n" \
                                 "id=\"{0}_{1}\"\n------------------\n".format(time.time(), randtext)

                    """ Find information by id mongodb"""
                    realnode = core.generalsearch('{ "_id": {id} }'.format(id=nodeid))

                    # Limit to 5 instance per block
                    thci = threading.Thread(name="Insert Instance",
                                       target=core.insert_instance,
                                       args=(realnode["name"], cluster["cluster"], str(count), command_id,))

                    thci.start()

                """ Wait all results of Thread from redis messages queue. Valid or not """
                timeout = 2 * int(generalconf["deploy"]["concurrencydeploy"]) * int(generalconf["deploy"]["delayrounddeploy"])
                for t in range(timeout):
                    time.sleep(1)
                    try:
                        if len(ast.literal_eval(redis_msg.get_message(command_id)["value"])) == int(count):
                            break
                    except BaseException as err:
                        print("Value not found", err)

                """ Return messages """
                return ast.literal_eval(redis_msg.get_message(command_id)["value"])
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "Invalid request: {0}".format(e)
            }
        return result

    def PUT(self, vmid):
        try:
            data = json.loads(web.data().decode('utf-8'))
            result = core.change_instances(vmid, data)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "Invalid request: {0}".format(e)
            }
        return result

    def DELETE(self, vmid):
        try:
            result = core.delete_instances(vmid)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "Invalid request: {0}".format(e)
            }
        return result


class ThreadAPI(threading.Thread):
    #def __init__(self, threadid, name, urls, c, g, r):
    def __init__(self, threadid, name, urls, c, g, logger):
        """ Pass Global var in this theard."""
        global core, generalconf, redis_msg
        core = c
        generalconf = g
        redis_msg = core.redis_msg

        """ RUN API """
        threading.Thread.__init__(self)
        self.threadID = threadid
        self.threadName = name
        self.app = HttpApi(urls, globals())
        self.app.notfound = notfound

    def run(self):
        print("Start API server...")
        self.app.run()

    def stop(self):
        print("Stop API server...")
        self.app.stop()


def notfound():
    return web.notfound({"value": "Bad request"})


class HttpApi(web.application):
    def run(self, ip="127.0.0.1", port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, (ip, int(port)))
