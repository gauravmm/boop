#!python3
import http.server
from pathlib import Path
from endpoints import ALL_ENDPOINTS, ERROR_500

SERVER_ADDR = ('', 8000)
PATH_WEB=Path("web/")

class BoopHTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # print(self.requestline)
        try:
            for endpt in ALL_ENDPOINTS:
                if endpt.canRun(self.path):
                    return endpt.run(path, self.wfile)
        except:
            ERROR_500.run(path, self.wfile)
        print(self.path)

def run():
    httpd = http.server.HTTPServer(SERVER_ADDR, BoopHTTPHandler)
    httpd.serve_forever()

run()
