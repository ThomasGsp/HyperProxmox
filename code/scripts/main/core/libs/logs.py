import logging
import argparse
import sys
import http.client as http_client
import datetime
import re


class StreamToLogger(object):
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


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


class Logger(object):
    def __init__(self, config):
        self.debug = config['common']['debug']
        self.error_log = config['common']['error_log']
        self.stdout_logger = None

    def run(self):
        # HTTP Debug (verbose !!)
        if self.debug is True:
            # Logging configuration INFO, DEBUG, ERROR
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s:%(levelname)s:%(name)s:%(threadName)s:%(message)s',
                filename=str(self.error_log),
                filemode='a'
            )

            http_client.HTTPConnection.debuglevel = 1
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.propagate = True
            sl = StreamToLogger(requests_log, str(self.debug))
            sys.stdout = sl

        else:
            # Logging configuration INFO, DEBUG, ERROR
            logging.basicConfig(
                level=logging.ERROR,
                format='%(asctime)s:%(levelname)s:%(name)s:%(threadName)s:%(message)s',
                filename=str(self.error_log),
                filemode='a'
            )

        loginlv = ["INFO", "WARNING", "ERROR", "CRITICAL", "DEBUG"]
        for lv in loginlv:
            self.stdout_logger = logging.getLogger(lv)
            sl = StreamToLogger(self.stdout_logger, logging.INFO)
            sys.stdout = sl

        return self.stdout_logger

    def write_error(self, node, errortxt, destfile):
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M")
        errortxt = re.sub(r"ticket\?(.*?) ", "ticket?username=***YOUR_USER***&password=***PWD***", errortxt)

        error = "[{date} -- {node}] : {error} \n".format(date=date, node=node, error=errortxt)
        errorlog = open(destfile, "ab")
        errorlog.write(error.encode('utf-8'))
        errorlog.close()


def vtype(verbose):
    switcher = {
        1: "INFO",
        2: "WARNING",
        3: "ERROR",
        4: "CRITICAL",
        5: "DEBUG"
    }
    return switcher.get(verbose, "DEBUG")
