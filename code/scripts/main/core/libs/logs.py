import logging
import argparse
import sys
import http.client as http_client
import datetime
import re
import json
from sys import getsizeof

class Logger:
    def __init__(self, loggerconf):
        self.logs_dir = loggerconf['logs_dir']
        self.log_level = int(loggerconf['logs_level'])
        self.bulk = loggerconf['bulk_write']
        self.bulk_size = loggerconf['bulk_size']
        self.currenttext_proxmox = ""
        self.currenttext_hyperproxmox = ""
        self.currenttext_python = ""
        self.currenttext_others = ""

    def write(self, json_text):
        switcher = {
            1: "INFO",
            2: "WARNING",
            3: "ERROR",
            4: "CRITICAL",
            5: "DEBUG"
        }

        lKeyC = [key for key, value in switcher.items() if '"{val}"'.format(val=value) == json.dumps(json_text["result"])][0]

        if lKeyC >= self.log_level or self.log_level == 5:

            now = datetime.datetime.now()
            date = now.strftime("%Y-%m-%d %H:%M")
            newtext = re.sub(r"ticket\?(.*?) ", "ticket?username=***YOUR_USER***&password=***PWD***", json.dumps(json_text["value"]))

            try:
                info = "[{3}] [{0}] [{1}] [{2}]".format(json_text["result"], json_text["type"], json_text["target"], json_text["thread"])
            except BaseException:
                info = "[{2}] [{0}] [{1}]".format(json_text["result"], json_text["type"], json_text["thread"])

            newtext = "[{date}] {info} : {text} \n".format(date=date, info=info, text=newtext)

            try:
                if json_text["type"] == "PROXMOX":
                    self.currenttext_proxmox = self.currenttext_proxmox + newtext
                    if getsizeof(self.currenttext_proxmox) > 800 or self.bulk == 0 or self.log_level == 5:
                        errorlog = open("{0}/proxmox.log".format(self.logs_dir), "ab")
                        errorlog.write(self.currenttext_proxmox.encode('utf-8'))
                        self.currenttext_proxmox = ""
                        errorlog.close()

                elif json_text["type"] == "HYPERPROXMOX":
                    self.currenttext_hyperproxmox = self.currenttext_hyperproxmox + newtext
                    if getsizeof(self.currenttext_hyperproxmox) > 800 or self.bulk == 0 or self.log_level == 5:
                        errorlog = open("{0}/hyperproxmox.log".format(self.logs_dir), "ab")
                        errorlog.write(self.currenttext_hyperproxmox.encode('utf-8'))
                        self.currenttext_hyperproxmox = ""
                        errorlog.close()

                elif json_text["type"] == "PYTHON":
                    self.currenttext_python = self.currenttext_python + newtext
                    if getsizeof(self.currenttext_python) > 800 or self.bulk == 0 or self.log_level == 5:
                        errorlog = open("{0}/python.log".format(self.logs_dir), "ab")
                        errorlog.write(self.currenttext_python.encode('utf-8'))
                        self.currenttext_python = ""
                        errorlog.close()
                else:
                    self.currenttext_others = self.currenttext_others + newtext
                    if getsizeof(self.currenttext_others) > 800 or self.bulk == 0 or self.log_level == 5:
                        errorlog = open("{0}/others.log".format(self.logs_dir), "ab")
                        errorlog.write(self.currenttext_others.encode('utf-8'))
                        self.currenttext_others = ""
                        errorlog.close()


            except BaseException:
                print("Cannot write on {0}, please check permissions.".format(self.logs_dir))
                exit(1)
