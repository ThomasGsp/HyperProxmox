#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 Author: Tlams
 Langage: Python
 Minimum version require: 3.4
"""

from pathlib import Path
from api.v1.api import *
from core.modules.mod_access import *
import configparser
import getpass
import os
import stat
import urllib3
global passhash
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if __name__ == "__main__":
    """ Read conf """
    localconf = configparser.ConfigParser()
    localconf.read('private/conf/config')

    CritConf = CryticalData()
    """ Step One: test private key or create it """
    key_pvt = Path(localconf['system']['key_pvt'])

    if not key_pvt.is_file():
        print("No key found, auto-generation started ...")
        passhash = encodepassphrase(getpass.getpass("Need a passphrase to start the generation:"))

        print("This action can take some minutes, please wait.")
        gen = CritConf.generate_key(localconf['system']['key_pvt'], localconf['system']['key_pub'], passhash)
        if gen['result'] == "OK":
            print("Your new key has been generate ! "
                  "\n - Private Key: {0} "
                  "\n - Public Key: {1}"
                  .format(localconf['system']['key_pvt'], localconf['system']['key_pvt']))
            print("Passphrase HASH: {0}".format(passhash))
            print("You must save your passphrase hash in a security place !")
        else:
            print(gen['Error'])
            exit(1)

    """ Test valid right for your private Key """
    if oct(stat.S_IMODE(os.stat(localconf['system']['key_pvt']).st_mode)) != oct(0o600):
        print("Your private key has not the good right({0})..."
              "This problem can be very critical for your security.".
              format(oct(stat.S_IMODE(os.stat(localconf['system']['key_pvt']).st_mode))))
        os.chmod(localconf['system']['key_pvt'], 0o600)
        print("Auto correction... done !")

    """ Step two"""
    if 'passhash' not in vars():
        passhash = encodepassphrase(getpass.getpass("This system need a passphrase to start:"))
        key_pvt = CritConf.read_private_key(localconf['system']['key_pvt'], passhash)
        if key_pvt['result'] != "OK":
            print("{0}: {1}"
                  "\n Please verify your passphrase".format(key_pvt['type'], key_pvt['error']))
            exit(1)

    key_pub = CritConf.read_public_key(localconf['system']['key_pub'])

    # URL MAPPING
    urls = \
        (
            # MAPPING INSTANCES
            '/api/v1/instance', 'Instance',
            '/api/v1/instance/new', 'Instance',
            '/api/v1/instance/([0-9]+)', 'Instance',
            '/api/v1/instance/([0-9]+)/status/([a-z]+)', 'Instance',

            '/api/v1/instance/([0-9]+)/package', 'package',
            '/api/v1/instance/([0-9]+)/vhost(?:/([0-9]+))', 'vhost',
            '/api/v1/instance/([0-9]+)/database(?:/([0-9]+))', 'database',

            #  MAPPING NODES
            '/api/v1/node(?:/([0-9]+))', 'node',

            # MAPPING SERVICES
            '/api/v1/service/([a-z]+)/instance/([0-9]+)/vhost(?:/([0-9]+))', 'service',

            # AUTH
            '/api/v1/auth', 'Auth',

            # MANAGEMENT
            '/api/v1/administration/cluster', 'Cluster',
            '/api/v1/administration/cluster/new', 'Cluster',

            # CACHE DATA (MONGO)
            # date/cluster/node/vmid
            '/api/v1/static/(instances)/([0-9]+)/([0-9a-zA-Z]+)/([0-9a-zA-Z]+)/([0-9]+)', 'QueryCache_Infra',
            '/api/v1/static/(instances)/([0-9]+)/([0-9a-zA-Z]+)/([0-9a-zA-Z]+)/', 'QueryCache_Infra',
            '/api/v1/static/(instances)/([0-9]+)/([0-9a-zA-Z]+)/', 'QueryCache_Infra',
            '/api/v1/static/(instances)/([0-9]+)/', 'QueryCache_Infra',

            # date/cluster/node
            '/api/v1/static/(nodes)/([0-9]+)/([0-9a-zA-Z]+)/([0-9a-zA-Z]+)', 'QueryCache_Infra',
            '/api/v1/static/(nodes)/([0-9]+)/([0-9a-zA-Z]+)/', 'QueryCache_Infra',
            '/api/v1/static/(nodes)/([0-9]+)/', 'QueryCache_Infra',

            # cluster
            '/api/v1/static/(clusters)/([0-9]+)/(?:[0-9a-zA-Z]+)',  'QueryCache_Infra',
            '/api/v1/static/(clusters)/([0-9]+)/', 'QueryCache_Infra',

            # date
            '/api/v1/static/dates/', 'QueryCache_Dates',

            # mongoid
            '/api/v1/static/(instances|nodes|clusters)/id/[a-z0-9]+', 'General_Search',

        )

    generalconf = {
        "keys": {"key_pvt": key_pvt["data"], "key_pub": key_pub["data"]},
        "mongodb": {"ip": localconf['databases']['mongodb_ip'], 'port': localconf['databases']['mongodb_port']},
        "redis": {"ip": localconf['databases']['redis_ip'], 'port': localconf['databases']['redis_port']},
        "deploy": {'concurrencydeploy': localconf['options']['concurrencydeploy'], 'delayrounddeploy': localconf['options']['delayrounddeploy']}
    }

    """ First redis connection """
    Lredis = Redis_messages(generalconf["redis"]["ip"])
    Lredis.connect()

    """ Init Core thread """
    core = Core(generalconf, Lredis)

    """ Init API thread """
    api_th = ThreadAPI(1, "ThreadAPI", urls, core, generalconf, Lredis)
    api_th.start()

