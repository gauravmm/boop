import json
import logging
import mimetypes
import urllib
from pathlib import Path

from pywebpush import WebPushException, webpush

from config import *

logger = logging.getLogger("boop.endpoints")

ALL_ENDPOINTS = []
class EndpointHandler(object):
    def __init__(self, name, endpt, func):
        self.name = name
        self.endpt = endpt
        self.func = func

    def canRun(self, path):
        return path.startswith(self.endpt)

    def run(self, path, wfile, **kwargs):
        wfile.write(self.func(path, **kwargs))

def error(errorid):
    if errorid not in ["404", "500"]:
        errorid = "500"
    return lambda _, **__: (PATH_WEB / ("error_" + errorid)).read_bytes()

ERROR_500 = EndpointHandler("500Error", "", error("500"))
ERROR_404 = EndpointHandler("404Error", "", error("404"))


#
# /register/<name>/<id>
#
def _reghandler(path, **kwargs):
    # Get the name from the path:
    path_parts = path.split("/", 3)
    name = path_parts[2]
    qs = urllib.parse.unquote_plus(path_parts[3])
    message = ""

    logger.info("Registering {} with querystring {}.".format(name, qs))
    message = kwargs["regMan"].setClient(name, qs)
    success = not message

    # Handle the generation of config.js
    rv = "HTTP/1.x 200 OK\nContent-Type: application/javascript\n\n"
    rv += json.dumps({ "success": success, "message": message })
    return rv.encode('utf-8')
ALL_ENDPOINTS.append(EndpointHandler("RegistrationHandler", "/register/", _reghandler))


#
# /config.js
#
def _confighandler(path, **kwargs):
    # Handle the generation of config.js
    rv = "HTTP/1.x 200 OK\n"
    rv += "Content-Type: application/javascript\n"
    rv += "\n"
    rv += "const CONFIG = " + json.dumps({
        "server_key": SERVER_KEY,
        "url": SERVER_URL
    })
    return rv.encode('utf-8')
ALL_ENDPOINTS.append(EndpointHandler("ConfigHandler", "/config.js", _confighandler))


#
# /**
#
def _filehandler(path, **kwargs):
    # Any errors raised are returned as HTTP/500 automatically.
    qpos = path.find("?")
    if qpos >= 0:
        path = path[:qpos]

    if path and path[0] == "/":
        path = path[1:]
    if not path or path == "":
        path = "index.html"
    abs_path = (PATH_WEB / path)
    assert abs_path.relative_to(PATH_WEB)

    if abs_path.exists():
        typ, enc = mimetypes.guess_type(str(abs_path))
        rv = "HTTP/1.x 200 OK\n"
        if typ:
            rv += "Content-Type: " + typ + "\n"
        if enc:
            rv += "Content-Encoding: " + enc + "\n"
        rv += "\n"
        
        return rv.encode('utf-8') + abs_path.read_bytes()
    else:
        return ERROR_404.func(path)
ALL_ENDPOINTS.append(EndpointHandler("FileHandler", "/", _filehandler))
