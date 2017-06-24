#!python3
import http.server
from pathlib import Path

from config import *
from endpoints import ALL_ENDPOINTS, ERROR_500


class BoopHTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            for endpt in ALL_ENDPOINTS:
                if endpt.canRun(self.path):
                    print("Serving {} with {}".format(self.path, endpt.name))
                    return endpt.run(self.path, self.wfile)
        except Exception as e:
            print(e)
            ERROR_500.run(self.path, self.wfile)
            raise
        print(self.path)

def run():
    httpd = http.server.HTTPServer(SERVER_ADDR, BoopHTTPHandler)
    httpd.serve_forever()

run()
