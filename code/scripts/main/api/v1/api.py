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


class Auth:
    def POST(self):
        # '{"username":"fff", "password":"azerty"}'
        data = json.loads(web.data().decode('utf-8'))
        print(data["username"])
        # Test Login

        # If true generate an ticket
        return

class Cluster:
    def GET(self, cluster=None):
        if cluster:
            return core.get_cluster(cluster)
        else:
            return core.get_cluster()

    def POST(self):
         data = json.loads(web.data().decode('utf-8'))
         return core.insert_cluster(data)

    def PUT(self, cluster):
        data = json.loads(web.data().decode('utf-8'))
        return core.change_cluster(cluster, data)

    def DELETE(self, cluster):
        return core.delete_cluste(cluster)


class Instance:
    def GET(self, vmid=None, status=None):
        if status:
            """ GET INSTANCE STATUS """
            return core.status_instance(vmid, status)
        elif vmid:
            """ GET INSTANCE INFORMATION """
            return core.info_instance(vmid)

    def POST(self, vmid=None, status=None):
        if vmid:
            """ GET INSTANCE INFORMATION """
            return core.status_instance(vmid, status)
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
            for target, count in sorted_nodes.items():
                # Limit to 5 instance per block
                thci = threading.Thread(name="Insert Instance",
                                   target=core.insert_instance,
                                   args=(target, str(count), command_id,))

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

    def PUT(self, vmid):
        data = json.loads(web.data().decode('utf-8'))
        return core.change_instance(vmid, data)

    def DELETE(self, vmid):
        return core.delete_instance(vmid)


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
