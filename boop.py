#!python3
import http.server
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from RegistrationManager import RegistrationManager
from config import *
from endpoints import ALL_ENDPOINTS, ERROR_500

#
# Logging
#
logfile = RotatingFileHandler(filename=PATH_LOG, backupCount=5, maxBytes=10240)
logfile.setLevel(logging.DEBUG)
logfile.setFormatter(logging.Formatter('[%(asctime)s, %(levelname)s @%(name)s] %(message)s'))
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('[%(asctime)s %(levelname)-3s @%(name)s] %(message)s', datefmt='%H:%M:%S'))
logging.basicConfig(level=logging.DEBUG, handlers=[logfile, console])
logger = logging.getLogger("boop")

#
# Registration Manager
#
notifyMan = RegistrationManager(CLIENT_MANAGER, MAX_CLIENTS)
pusherMan = RegistrationManager(PUSHER_MANAGER, MAX_CLIENTS)

#
# Handler
#
class BoopHTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        kwargs = {
            "rfile": self.rfile,
            "headers": self.headers,
            "clients": notifyMan,
            "pushers": pusherMan,
        }
        try:
            for endpt in ALL_ENDPOINTS:
                if endpt.canRun(self.path):
                    logger.debug("Serving {} with {}".format(self.path, endpt.name))
                    return endpt.run(self.path, self.wfile, **kwargs)
        except Exception as e:
            logger.exception(e)
            ERROR_500.run(self.path, self.wfile, **kwargs)
            raise
        print(self.path)


#
# Init
#
def run():
    logger.info("Started Boop.")
    logger.info("Location: " + SERVER_URL)
    logger.info("Server Key: " + SERVER_KEY)

    httpd = http.server.HTTPServer(SERVER_ADDR, BoopHTTPHandler)
    httpd.serve_forever()

run()
