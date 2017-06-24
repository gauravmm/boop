from pathlib import Path

from pywebpush import WebPushException, webpush

ALL_ENDPOINTS = []
class EndpointHandler(object):
    def __init__(self, name, endpt, func):
        self.name = name
        self.endpt = endpt
        self.run = func

    def canRun(self, path):
        return path.startsWith(self.endpt)

    def run(self, path, wfile):
        wfile.write(self.func(path))

    def register(self):
        ALL_ENDPOINTS.append(self)

def error(errorid, wfile):
    if errorid not in ["404", "500"]:
        errorid = "500"
    return (PATH_WEB / ("error_" + errorid)).read_bytes()

ERROR_500 = EndpointHandler("500Error", "", lambda _: error("500", wfile))
ERROR_404 = EndpointHandler("404Error", "", lambda _: error("404", wfile))