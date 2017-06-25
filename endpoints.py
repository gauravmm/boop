import base64
import hashlib
import json
import logging
import mimetypes
import time
import urllib
import uuid
from pathlib import Path

from config import *
from objects import Client, Pusher
from pywebpush import WebPushException, webpush

logger = logging.getLogger("boop.endpoints")

ALL_ENDPOINTS = []

timestamp = lambda: int(time.time())

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

def returnStr(inp):
    return ("HTTP/1.1 200 OK\nContent-Type: application/javascript\n\n" + inp).encode('utf-8')
def returnJSON(inp):
    return returnStr(json.dumps(inp))

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

            # logger.debug("Processing /{}/ with args: {}".format(nm, ",".join(path_parts)))
            args = []
            nargs = len(path_parts)
            if vars and vars[-1] == "*":
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

authstr = "Basic " + base64.b64encode((AUTH_USERNAME + ":" + AUTH_PASSWORD).encode("utf-8")).decode("utf-8")
def httpAuth(func):
    def checkAuthHeaders(h):
        if "Authorization" not in h:
            return False
        if h["Authorization"].strip() == authstr:
            logger.info("Failed auth" + h["Authorization"].strip() + " vs " + authstr)
            return True
        return False

    def func_wrapper(*args, **kwargs):
        if not AUTH_ENABLE or checkAuthHeaders(kwargs["headers"]):
            return func(*args, **kwargs)
        # Return the authentication request headers:
        return ("HTTP/1.1 401 Access Denied\n" + \
            "WWW-Authenticate: Basic realm=\"Boop\"\n" + \
            "Content-Length: 0\n\n").encode("utf-8")

    return func_wrapper


#
# /register/<name>/<subscription>
#
@parsePath("register", ["name", "sub"])
def _reghandler(name, sub, **kwargs):
    sub = json.loads(sub)
    logger.debug("Registering {} with subscription {}.".format(name, sub))
    message = kwargs["clients"].put(name, Client(name, timestamp(), sub))
    return returnJSON({"success": not message, "message": message})
ALL_ENDPOINTS.append(EndpointHandler("RegistrationHandler", "/register/", _reghandler))


#
# /touch/<name>
#
@parsePath("touch", ["name"])
def _touchhandler(name, **kwargs):
    logger.debug("Touch {}.".format(name))
    try:
        kwargs["clients"].touch(name, timestamp())
    except Exception as e:
        logger.exception(e)
    return returnJSON({"success": True, "message": ""})
ALL_ENDPOINTS.append(EndpointHandler("AcknowledgementHandler", "/touch/", _touchhandler))


#
# /addpusher/name/
#
@httpAuth
@parsePath("addpusher", ["name"])
def _addpusherhandler(name, **kwargs):
    auth = str(uuid.uuid4())
    logger.debug("Adding Pusher {} with auth {}.".format(name, auth))
    message = kwargs["pushers"].put(name, Pusher(name, timestamp(), auth))
    return returnJSON({"success": not message, "message": message, "auth": auth})
ALL_ENDPOINTS.append(EndpointHandler("AddPusherHandler", "/addpusher/", _addpusherhandler))

#
# /remove/<client|pusher>/name/
#
@httpAuth
@parsePath("remove", ["pushers", "name"])
def _removeconn(clpu, name, **kwargs):
    if clpu == "pushers":
        msg = kwargs[clpu].put(name, None)
        if not msg:
            # If we removed it successfully, then we check if the other regman has it.
            # If it does not have it, then we can remove it from styleman:
            if not kwargs["clients"].get(name):
                kwargs["styles"].anull(name)
    else:
        msg = "Can only remove pushers."
    return returnJSON({ "success": not msg, "message": msg })
ALL_ENDPOINTS.append(EndpointHandler("RemoveConnectionHandler", "/remove/", _removeconn))



#
# /getconn/
#
@httpAuth
@parsePath("getconn", [])
def _getconn(**kwargs):
    return returnJSON({
        "success": True,
        "message": "",
        "clients": [v.getData(**kwargs) for v in kwargs["clients"].values()],
        "pushers": [v.getData(**kwargs) for v in kwargs["pushers"].values()]
    })
ALL_ENDPOINTS.append(EndpointHandler("GetConnectionHandler", "/getconn/", _getconn))


#
# /push/name/sig/title/text/[args/]*
#
def _warnOut(s):
    logger.warn(s.strip())
    return returnStr(s)

@parsePath("push", ["pusher_name", "sig", "timestamp", "title", "text", "*"])
def _pushhandler(name, sig, timest, title, text="", *args, **kwargs):
    # Look up name to get secret
    try:
        secret = kwargs["pushers"].get(name).secret
    except:
        return _warnOut("Pusher '{}' is not registered.\n".format(name))

    # Check if secret is correct:
    sig_calc = hashlib.sha224(
        "{}/{}/".format(secret,"/".join(kwargs["original_path_parts"][2:])).encode('utf-8')).hexdigest()
    if sig_calc != sig:
        return _warnOut("Signature error.\n")

    # Check if this was signed within the last MAX_DELAY seconds.
    now = timestamp()
    if (now - int(timest)) > MAX_DELAY:
        return _warnOut("Delay error.\n")

    logger.info("Pushing {}: {}.".format(title, text))

    kwargs["pushers"].touch(name, now)

    notif = {
        "title": title,
        "body": text,
        "url": SERVER_URL,
        "badge": "icons/bell.png",
        "icon": "icons/bell-solid.png",
        "args": args
    }

    for sub in kwargs["clients"].values():
        notif["acknowledge_url"] = "{}touch/{}/".format(SERVER_URL, sub.name)
        webpush(
            sub.subscription,
            json.dumps(notif).encode('utf-8'),
            vapid_private_key=PATH_PEM,
            vapid_claims={"sub": "mailto:" + ADMIN_EMAIL})

    return returnStr("")
ALL_ENDPOINTS.append(EndpointHandler("PushHandler", "/push/", _pushhandler))


#
# /config.js
#
@httpAuth
def _confighandler(path, **kwargs):
    # Handle the generation of config.js
    rv = "HTTP/1.x 200 OK\n"
    rv += "Content-Type: application/javascript\n"
    rv += "\n"
    rv += "const CONFIG = " + json.dumps({
        "server_key": SERVER_KEY,
        "url": SERVER_URL,
        "auth": authstr
    })
    return rv.encode('utf-8')
ALL_ENDPOINTS.append(EndpointHandler("ConfigHandler", "/config.js", _confighandler))


#
# /**
#
@httpAuth
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
        rv = "HTTP/1.1 200 OK\n"
        if typ:
            rv += "Content-Type: " + typ + "\n"
        if enc:
            rv += "Content-Encoding: " + enc + "\n"
        rv += "\n"
        
        return rv.encode('utf-8') + abs_path.read_bytes()
    else:
        return ERROR_404.func(path)
ALL_ENDPOINTS.append(EndpointHandler("FileHandler", "/", _filehandler))
