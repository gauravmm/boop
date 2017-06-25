# Class Defs

import logging
import pickle
from collections import OrderedDict
from pathlib import Path

from config import STYLE_COLOR, STYLE_IMAGE, STYLE_CLASS

logger = logging.getLogger("boop.regman")

class RegManager(object):
    def __init__(self, regFile, max_clients=20):
        self.fn = Path(regFile)
        self.max_clients = max_clients
        
        try:
            self.clients = pickle.loads(self.fn.read_bytes())
        except:
            logger.warn("Client database does not exist or cannot be read. Starting with empty database.")
            self.clients = {}

    def put(self, name, val):
        if not val:
            if name in self.clients:
                del self.clients[name]
            else:
                return "Server has no record of client."
        elif name not in self.clients and len(self.clients) >= self.max_clients:
            return "Server will not accept any more clients."
        else:
            self.clients[name] = val
        self.fn.write_bytes(pickle.dumps(self.clients))
        return None

    def touch(self, name, timestamp):
        v = self.get(name)
        if v:
            v.lastseen = timestamp

    def get(self, name):
        try:
            return self.clients[name]
        except KeyError:
            return None

    def values(self):
        return self.clients.values()

    def keys(self):
        return self.clients.keys()

    def __repr__(self):
        return self.clients.__repr__()


class StyleManager(object):
    def __init__(self, fn, max_clients=20):
        self.fn=Path(fn)
        self.idx = 0
        self.max_clients = max_clients
        try:
            self.names = pickle.loads(self.fn.read_bytes())
        except:
            logger.warn("StyleManager database does not exist or cannot be read. Starting with empty database.")
            self.names = []
    
    def get(self, name):
        try:
            idx = self.names.index(name)
        except:
            # First try to find the first deleted slot
            try:
                idx = self.names.index(None)
            except:
                idx = len(self.names)

            if idx <= self.max_clients:
                self.names.append(name)
                self.fn.write_bytes(pickle.dumps(self.names))

        idx = idx % len(STYLE_IMAGE)
        return {
            "icon": STYLE_IMAGE[idx],
            "color": STYLE_COLOR[idx],
            "class": STYLE_CLASS[idx]
        }

    def anull(self, name):
        try:
            idx = self.names.index(name)
            self.names[idx] = None
        except:
            pass

class Client(object):
    def __init__(self, name, created, subscription, browser="", machine=""):
        self.name = name
        self.created = created
        self.lastseen = created
        self.subscription = subscription
        self.browser = browser
        self.machine = machine

    def getData(self, **kwargs):
        rv = {k: self.__getattribute__(k) for k in ["name", "created", "lastseen", "browser", "machine"]}
        rv["style"] = kwargs["styles"].get(self.name)
        return rv


class Pusher(object):
    def __init__(self, name, created, secret):
        self.name = name
        self.created = created
        self.lastseen = created
        self.secret = secret

    def getData(self, **kwargs):
        rv = {k: self.__getattribute__(k) for k in ["name", "lastseen", "created"]}
        rv["style"] = kwargs["styles"].get(self.name)
        return rv
