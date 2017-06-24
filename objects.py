# Class Defs

import logging
import pickle
from collections import OrderedDict
from pathlib import Path

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


class Client(object):
    def __init__(self, name, created, subscription, browser="", machine=""):
        self.name = name
        self.created = created
        self.subscription = subscription
        self.browser = browser
        self.machine = machine

    def getData(self):
        return {k: self.__getattribute__(k) for k in ["name", "created", "browser", "machine"]}


class Pusher(object):
    def __init__(self, name, created, secret):
        self.name = name
        self.created = created
        self.secret = secret

    def getData(self):
        return {k: self.__getattribute__(k) for k in ["name", "created"]}
