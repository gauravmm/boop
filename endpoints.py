import hashlib
import json
import logging
import mimetypes
import urllib
import uuid
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

def returnJSON(inp):
    rv = "HTTP/1.1 200 OK\nContent-Type: application/javascript\n\n"
    rv += json.dumps(inp)
    return rv.encode('utf-8')

def parsePath(nm, vars):
    def decorate(func):
        def func_wrapper(path, **kwargs):
            path_parts = path.split("/", 99)
            assert path_parts[0] == ""
            assert path_parts[1] == nm
            if path_parts[-1] == "":
                path_parts.pop()
            kwargs["original_path_parts"]=path_parts[2:]
            path_parts = [urllib.parse.unquote_plus(p) for p in path_parts[2:]]

            args = []
            nargs = len(path_parts)
            if vars[-1] == "*":
                nargs -= 1
                args=path_parts[nargs:]
                path_parts=path_parts[:nargs]

            if len(path_parts) >= nargs:
                return func(*path_parts, *args, **kwargs)
            else:
                return returnJSON({
                    "success": False,
                    "message": "Incorrect format. We expect {}/{}/{}".format(SERVER_URL, nm, "/".join("&lt;"+v+"&gt;" for v in vars))
                })
        return func_wrapper
    return decorate 


#
# /register/<name>/<subscription>
#
@parsePath("register", ["name", "sub"])
def _reghandler(name, sub, **kwargs):
    sub = json.loads(sub)
    logger.info("Registering {} with subscription {}.".format(name, sub))
    message = kwargs["clients"].put(name, sub)
    success = not message

    return returnJSON({"success": success, "message": message})
ALL_ENDPOINTS.append(EndpointHandler("RegistrationHandler", "/register/", _reghandler))


#
# /addpusher/name/
#
@parsePath("addpusher", ["name"])
def _addpusherhandler(name, **kwargs):
    auth = str(uuid.uuid4())
    logger.info("Adding Pusher {} with auth {}.".format(name, auth))
    message = kwargs["pushers"].put(name, auth)
    success = not message

    return returnJSON({"success": success, "message": message, "auth": auth})
ALL_ENDPOINTS.append(EndpointHandler("AddPusherHandler", "/addpusher/", _addpusherhandler))


#
# /push/name/sig/title/text/[args/]*
#
@parsePath("push", ["pusher_name", "sig", "title", "text", "*"])
def _pushhandler(name, sig, title, text="", *args, **kwargs):
    logger.info("Pushing {}: {}.".format(title, text))

    logger.warn(kwargs["original_path_parts"])
    # Look up name to get secret
    secret = kwargs["pushers"].get(name)
    if not secret:
        return "Pusher '{}' is not registered.\n"
    # Check if secret is correct:
    sig_calc = hashlib.sha224(
        "{}/{}/".format(secret,"/".join(kwargs["original_path_parts"][2:])).encode('utf-8')).hexdigest()
    if sig_calc != sig:
        return "Signature error.\n"

    notif = {
        "title": title,
        "body": text,
        "url": SERVER_URL,
        "badge": "icons/bell.png",
        "icon": "icons/bell-solid.png",
        "args": args
    }

    notif = json.dumps(notif).encode('utf-8')
    for sub in kwargs["clients"].values():
        webpush(
            sub,
            notif,
            vapid_private_key=PATH_PEM,
            vapid_claims={"sub": "mailto:" + ADMIN_EMAIL})

    return ""
ALL_ENDPOINTS.append(EndpointHandler("PushHandler", "/push/", _pushhandler))


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
