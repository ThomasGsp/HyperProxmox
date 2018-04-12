import logging
import argparse
import sys
import http.client as http_client
import datetime
import re
import json
from sys import getsizeof

class StreamToLogger(object):
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())


"""
class VAction(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        # print 'values: {v!r}'.format(v=values)
        if values is None:
            values = '1'
        try:
            values = int(values)
        except ValueError:
            values = values.count('v') + 1
        setattr(args, self.dest, values)
"""


class Logger(object):
    def __init__(self, generalconf):
        self.debug = generalconf['logger']['debug']
        self.logs_dir = generalconf['logger']['logs_dir']
        self.debug_level = generalconf['logger']['debug_level']
        self.stdout_logger = None

    def run(self):
        # HTTP Debug (verbose !!)
        if self.debug is True:
            # Logging configuration INFO, DEBUG, ERROR
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s:%(levelname)s:%(name)s:%(threadName)s:%(message)s',
                filename="{0}/debug.log".format(self.logs_dir),
                filemode='a'
            )

            http_client.HTTPConnection.debuglevel = 1
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.propagate = True
            sl = StreamToLogger(self.stdout_logger, logging.DEBUG)
            sys.stdout = sl

        else:
            # Logging configuration INFO, DEBUG, ERROR
            logging.basicConfig(
                level=logging.ERROR,
                format='%(asctime)s:%(levelname)s:%(name)s:%(threadName)s:%(message)s',
                filename="{0}/errors.log".format(self.logs_dir),
                filemode='a'
            )

        loginlv = ["INFO", "WARNING", "ERROR", "CRITICAL", "DEBUG"]
        for lv in loginlv:
            self.stdout_logger = logging.getLogger(lv)
            sl = StreamToLogger(self.stdout_logger, logging.INFO)
            sys.stdout = sl

        return self.stdout_logger

    def logsout(self, node, errortxt):
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M")
        errortxt = re.sub(r"ticket\?(.*?) ", "ticket?username=***YOUR_USER***&password=***PWD***", errortxt)

        error = "[{date} -- {node}] : {error} \n".format(date=date, node=node, error=errortxt)
        errorlog = open("{0}/proxmox.log".format(self.logs_dir), "ab")
        errorlog.write(error.encode('utf-8'))
        errorlog.close()




class Logger2:
    def __init__(self, loggerconf):
        self.logs_dir = loggerconf['logs_dir']
        self.log_level = int(loggerconf['logs_level'])
        self.bulk = loggerconf['bulk_write']
        self.bulk_size = loggerconf['bulk_size']
        self.currenttext = ""

    def write(self, json_text):
        switcher = {
            1: "INFO",
            2: "WARNING",
            3: "ERROR",
            4: "CRITICAL",
            5: "DEBUG"
        }

        lKeyC = [key for key, value in switcher.items() if '"{val}"'.format(val=value) == json.dumps(json_text["result"])][0]

        if lKeyC >= self.log_level and lKeyC <= 4:
            now = datetime.datetime.now()
            date = now.strftime("%Y-%m-%d %H:%M")
            newtext = re.sub(r"ticket\?(.*?) ", "ticket?username=***YOUR_USER***&password=***PWD***", json_text["value"])

            try:
                info = "[{0}] [{1}] [{2}]".format(json_text["result"], json_text["type"], json_text["target"])
            except BaseException:
                info = "[{0}] [{1}]".format(json_text["result"], json_text["type"])

            newtext = "[{date}] {info} : {text} \n".format(date=date, info=info, text=newtext)
            self.currenttext = self.currenttext + newtext

            if getsizeof(self.currenttext) > 800 or self.bulk == 0 or self.log_level == 6:
                try:
                    if json_text["type"] == "PROXMOX":
                        errorlog = open("{0}/proxmox.log".format(self.logs_dir), "ab")
                        errorlog.write(self.currenttext.encode('utf-8'))
                    elif json_text["type"] == "HYPERPROXMOX":
                        errorlog = open("{0}/hyperproxmox.log".format(self.logs_dir), "ab")
                        errorlog.write(self.currenttext.encode('utf-8'))
                    elif json_text["type"] == "PYTHON":
                        errorlog = open("{0}/python.log".format(self.logs_dir), "ab")
                        errorlog.write(self.currenttext.encode('utf-8'))
                    else:
                        errorlog = open("{0}/others.log".format(self.logs_dir), "ab")
                        errorlog.write(self.currenttext.encode('utf-8'))
                    errorlog.close()
                    self.currenttext = ""
                except BaseException:
                    print("Cannot write on {0}, please check permissions.".format(self.logs_dir))
                    exit(1)
