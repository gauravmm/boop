#!python3

import http.server

SERVER_ADDR = ('', 8000)

def run():
    # handler_class=BaseHTTPRequestHandler
    httpd = http.server.HTTPServer(SERVER_ADDR, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

run()