import mimetypes
from pathlib import Path

from pywebpush import WebPushException, webpush

from config import *

ALL_ENDPOINTS = []
class EndpointHandler(object):
    def __init__(self, name, endpt, func):
        self.name = name
        self.endpt = endpt
        self.func = func

    def canRun(self, path):
        return path.startswith(self.endpt)

    def run(self, path, wfile):
        wfile.write(self.func(path))

def error(errorid):
    if errorid not in ["404", "500"]:
        errorid = "500"
    return lambda _: (PATH_WEB / ("error_" + errorid)).read_bytes()

ERROR_500 = EndpointHandler("500Error", "", error("500"))
ERROR_404 = EndpointHandler("404Error", "", error("404"))

def _filehandler(path):
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
