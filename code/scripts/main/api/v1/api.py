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


def cooktheticket(ticket, action, target):
    if ticket == "aaa":
        return True
    else:
        return False

class Auth:
    def POST(self):
        # '{"username":"fff", "password":"azerty"}'
        data = json.loads(web.data().decode('utf-8'))
        print(data["username"])
        # Test Login

        # If true generate an ticket
        # use date and ip
        i = web.input(ticket='aaa')
        web.setcookie('ticket', i.ticket, 3600)
        return



""" CLASS MONGO CACHE """


class General_Search:
    def GET(self, query, id):
        try:
            return core.generalsearch(query, id)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "{0} {1}".format("Invalid request:", e)
            }
        return result

class QueryCache_Infra:
    def GET(self, dest, date, cluster=None, node=None, vmid=None):
        try:
            result = core.generalquerycacheinfra(dest, date, cluster, node, vmid)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "{0} {1}".format("Invalid request:", e)
            }
        return result




class Static_Nodes:
    def GET(self, date, cluster=None, node=None):
        if node and cluster:
            return core.generalsearch('{ "date": {0}, "cluster": {1},  "node": {2} }'.format(date, cluster, node))
        elif cluster:
            return core.generalsearch('{ "date": {0}, "cluster": {1} }'.format(date, cluster))
        else:
            return core.generalsearch('{ "date": {0}}'.format(date))


class Dates:
    def GET(self):
        return core.generalsearch('{ "_id": {id} }'.format(id=nodeid))


""" CLASS DIRECT """
class Cluster:
    def GET(self, cluster=None):
        try:
            if cluster:
                result = core.get_cluster(cluster)
            else:
                result = core.get_cluster()
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "{0} {1}".format("Invalid request:", e)
            }
        return result

    def POST(self):
        try:
            data = json.loads(web.data().decode('utf-8'))
            result = core.insert_cluster(data)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "{0} {1}".format("Invalid request:", e)
            }
        return result

    def PUT(self, cluster):
        try:
            data = json.loads(web.data().decode('utf-8'))
            result = core.change_cluster(cluster, data)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "{0} {1}".format("Invalid request:", e)
            }
        return result

    def DELETE(self, cluster):
        try:
            result = core.delete_cluste(cluster)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "{0} {1}".format("Invalid request:", e)
            }
        return result


class Instance:
    def GET(self, vmid, status=None):
        try:
            if status:
                """ GET INSTANCE STATUS """
                result = core.status_instance(vmid, status)
            else:
                """ GET INSTANCE INFORMATION """
                result = core.info_instance(vmid)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "Invalid request: {0}".format(e)
            }
        return result

    def POST(self, vmid=None, status=None):
        try:
            if vmid:
                """ GET INSTANCE INFORMATION """
                result = core.status_instance(vmid, status)
            else:
                """ CREATE NEWS INSTANCES"""
                count = json.loads(web.data().decode('utf-8'))["count"]

                """ GENERATE UNIQ COMMAND ID """
                randtext = ''.join(random.choice('0123456789ABCDEF') for i in range(8))
                command_id = "{0}_{1}_{2}".format(time.time(), count, randtext)

                """ LOAD CLUSTER CONFIGURATIONS """
                select = Analyse(core.clusters_conf, generalconf)
                sorted_nodes = dict(select.set_attribution(count))

                """ START ALL Thread """
                for nodeid, count in sorted_nodes.items():
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
                        if len(ast.literal_eval(Lredis.get_message(command_id))) == int(count):
                            break
                    except BaseException as err:
                        print("Value not found", err)

                """ Return messages """
                return ast.literal_eval(Lredis.get_message(command_id))
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "{0} {1}".format("Invalid request:", e)
            }
        return result

    def PUT(self, vmid):
        try:
            data = json.loads(web.data().decode('utf-8'))
            result = core.change_instance(vmid, data)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "{0} {1}".format("Invalid request:", e)
            }
        return result

    def DELETE(self, vmid):
        try:
            result = core.delete_instance(vmid)
        except BaseException as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - API",
                "value": "{0} {1}".format("Invalid request:", e)
            }
        return result


class ThreadAPI(threading.Thread):
    def __init__(self, threadid, name, urls, c, g, r):
        """ Pass Global var in this theard."""
        global core, generalconf, Lredis
        core = c
        generalconf = g
        Lredis = r

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
