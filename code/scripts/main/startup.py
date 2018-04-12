#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 Author: Tlams
 Langage: Python
 Minimum version require: 3.4
"""

from pathlib import Path
from api.v1.api import *
from core.libs.logs import *
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

    generalconf = {
        "logger": {"debug": localconf['logger']['debug'], "logs_level": localconf['logger']['logs_level'],
                   "logs_dir": localconf['logger']['logs_dir'], "bulk_write": localconf['logger']['bulk_write'],
                   "bulk_size": localconf['logger']['bulk_size']},

        "analyst": {"walker": localconf['walker']['walker'], "walker_lock": localconf['walker']['walker_lock']},

        "mongodb": {"ip": localconf['databases']['mongodb_ip'], 'port': localconf['databases']['mongodb_port']},

        "redis": {"ip": localconf['databases']['redis_ip'], 'port': localconf['databases']['redis_port']},

        "deploy": {'concurrencydeploy': localconf['deploy']['concurrencydeploy'],
                   'delayrounddeploy': localconf['deploy']['delayrounddeploy']}
    }

    """ Active logger"""
    logger = Logger2(generalconf["logger"])
    logger.write({"result": "INFO", "type": "HYPERPROXMOX", "value": "Start logger"})
    logger.write({"result": "INFO", "type": "HYPERPROXMOX", "value": ">>>>>>> -- NEW STARTUP -- <<<<<<<"})

    CritConf = CryticalData()
    """ Step One: test private key or create it """
    key_pvt = Path(localconf['system']['key_pvt'])

    if not key_pvt.is_file():
        print("No key found, auto-generation started ...")
        passhash = encodepassphrase(getpass.getpass("Need a passphrase to start the generation:"))

        print("This action can take some minutes, please wait.")
        gen = CritConf.generate_key(localconf['system']['key_pvt'], localconf['system']['key_pub'], passhash)
        if gen['result'] == "OK":
            logger.write({"result": "INFO", "type": "HYPERPROXMOX", "value": "Key generated in {0}".format(localconf['system']['key_pvt'])})
            print("Your new key has been generate ! "
                  "\n - Private Key: {0} "
                  "\n - Public Key: {1}"
                  .format(localconf['system']['key_pvt'], localconf['system']['key_pub']))
            print("Passphrase HASH: {0}".format(passhash))
            print("You MUST save your passphrase hash in a security place !")
            key_pvt = CritConf.read_private_key(localconf['system']['key_pvt'], passhash)
        else:
            print(gen['Error'])
            logger.write({"result": "ERROR", "type": "HYPERPROXMOX", "value": "Your key is not create due to an error: {0}".format(gen['value'])})
            exit(1)

    """ Test valid right for your private Key """
    if oct(stat.S_IMODE(os.stat(localconf['system']['key_pvt']).st_mode)) != oct(0o600):
        print("Your private key has not the good right({0})..."
              "This problem can be very critical for your security.".
              format(oct(stat.S_IMODE(os.stat(localconf['system']['key_pvt']).st_mode))))
        os.chmod(localconf['system']['key_pvt'], 0o600)
        print("Auto correction... done !")
        logger.write({"result": "INFO", "type": "HYPERPROXMOX",  "value": "Setting chmod on your key.."})

    """ Step two"""
    if 'passhash' not in vars():
        passhash = getpass.getpass("This system need a passphrase to start:")
        key_pvt = CritConf.read_private_key(localconf['system']['key_pvt'], passhash)
        if key_pvt['result'] != "OK":
            print("{0}: {1}"
                  "\n Please verify your passphrase".format(key_pvt['type'], key_pvt['error']))
            logger.write({"result": "WARNING", "type": "HYPERPROXMOX", "value": "Bad passphrase, try again."})
            exit(1)

    logger.write({"result": "INFO", "type": "HYPERPROXMOX", "value": "Loading keys in memory"})
    key_pub = CritConf.read_public_key(localconf['system']['key_pub'])
    generalconf["keys"] = {"key_pvt": key_pvt["value"], "key_pub": key_pub["value"]}

    # URL MAPPING
    urls = \
        (
            # FRESH DATA
            # MAPPING INSTANCES
            '/api/v1/instance', 'Instance',
            '/api/v1/instance/new', 'Instance',
            '/api/v1/instance/([0-9]+)', 'Instance',
            '/api/v1/instance/id/([a-z0-9]+)/status/(start|stop|current|reset|shutdown)', 'Instance',

            # AUTH
            '/api/v1/login', 'Login'

            # MANAGEMENT CLUSTER
            '/api/v1/administration/cluster/(?:[0-9a-zA-Z\_\-]+)', 'Cluster',
            '/api/v1/administration/cluster/', 'Cluster',
            # '/api/v1/administration/cluster/new', 'Cluster',

            # CACHE DATA (MONGO)
            # date/cluster/node/vmid
            # Disks mapping
            '/api/v1/static/(disks)/([0-9]+)/([0-9a-zA-Z\_\-]+)/([0-9a-zA-Z\_\-]+)/([0-9]+)', 'QueryCache_Infra',
            '/api/v1/static/(disks)/([0-9]+)/([0-9a-zA-Z\_\-]+)/([0-9a-zA-Z\_\-]+)/', 'QueryCache_Infra',
            '/api/v1/static/(disks)/([0-9]+)/([0-9a-zA-Z\_\-]+)/', 'QueryCache_Infra',
            '/api/v1/static/(disks)/([0-9]+)/', 'QueryCache_Infra',

            # Storages mapping
            '/api/v1/static/(storages)/([0-9]+)/([0-9a-zA-Z\_\-]+)/([0-9a-zA-Z\_\-]+)/', 'QueryCache_Infra',
            '/api/v1/static/(storages)/([0-9]+)/([0-9a-zA-Z\_\-]+)/', 'QueryCache_Infra',
            '/api/v1/static/(storages)/([0-9]+)/', 'QueryCache_Infra',

            # Instances mapping
            '/api/v1/static/(instances)/([0-9]+)/([0-9a-zA-Z\_\-]+)/([0-9a-zA-Z\_\-]+)/([0-9]+)', 'QueryCache_Infra',
            '/api/v1/static/(instances)/([0-9]+)/([0-9a-zA-Z\_\-]+)/([0-9a-zA-Z\_\-]+)/', 'QueryCache_Infra',
            '/api/v1/static/(instances)/([0-9]+)/([0-9a-zA-Z\_\-]+)/', 'QueryCache_Infra',
            '/api/v1/static/(instances)/([0-9]+)/', 'QueryCache_Infra',

            # Nodes mapping
            '/api/v1/static/(nodes)/([0-9]+)/([0-9a-zA-Z\_\-]+)/([0-9a-zA-Z\_\-]+)', 'QueryCache_Infra',
            '/api/v1/static/(nodes)/([0-9]+)/([0-9a-zA-Z\_\-]+)/', 'QueryCache_Infra',
            '/api/v1/static/(nodes)/([0-9]+)/', 'QueryCache_Infra',

            # cluster mapping
            '/api/v1/static/(clusters)/([0-9]+)/(?:[0-9a-zA-Z\_\-]+)',  'QueryCache_Infra',
            '/api/v1/static/(clusters)/([0-9]+)/', 'QueryCache_Infra',

            # date
            '/api/v1/static/dates/(all|last)', 'QueryDates',

            # mongoid
            '/api/v1/static/(instances|nodes|clusters|storages|disks)/id/([a-z0-9]+)', 'General_Search',

        )

    """ Init Core thread """
    logger.write({"result": "INFO", "type": "HYPERPROXMOX", "value": "Init Core thread"})
    core = Core(generalconf)

    """ Init API thread """
    logger.write({"result": "INFO", "type": "HYPERPROXMOX", "value": "Init API thread"})
    api_th = ThreadAPI(1, "ThreadAPI", urls, core, generalconf)
    api_th.start()