#!python3
import http.server
from pathlib import Path

import logging
from logging.handlers import RotatingFileHandler
from config import *
from endpoints import ALL_ENDPOINTS, ERROR_500

# Logging
logfile = RotatingFileHandler(filename=PATH_LOG, backupCount=5, maxBytes=10240)
logfile.setLevel(logging.DEBUG)
logfile.setFormatter(logging.Formatter('[%(asctime)s, %(levelname)s @%(name)s] %(message)s'))
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('[%(asctime)s %(levelname)-3s @%(name)s] %(message)s', datefmt='%H:%M:%S'))
logging.basicConfig(level=logging.DEBUG, handlers=[logfile, console])
logger = logging.getLogger("boop")

class BoopHTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            for endpt in ALL_ENDPOINTS:
                if endpt.canRun(self.path):
                    logger.debug("Serving {} with {}".format(self.path, endpt.name))
                    return endpt.run(self.path, self.wfile)
        except Exception as e:
            logger.exception(e)
            ERROR_500.run(self.path, self.wfile)
            raise
        print(self.path)

def run():
    logger.info("Started Boop.")
    logger.info("Location: " + SERVER_URL)
    logger.info("Server Key: " + SERVER_KEY)

    httpd = http.server.HTTPServer(SERVER_ADDR, BoopHTTPHandler)
    httpd.serve_forever()

run()
