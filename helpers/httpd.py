#!/usr/bin/env python

import ssl
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

## Certificate Generation:
# openssl req -new -x509 -keyout test.pem -out test.pem -days 365 -nodes

#Create custom HTTPRequestHandler class
class HuePiRequestHandler(BaseHTTPRequestHandler):
    # handle POST command
    def do_POST(self):
        pass

    #handle GET command
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("Oh, Hello, world!")
        except:
            self.send_error(500, 'Server error')


print("Starting HTTP Server...")
#ip and port of servr
server_address = ('', 4443)
cert = './test.pem'
httpd = HTTPServer(server_address, HuePiRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket, certfile=cert, server_side=True)
httpd.serve_forever()
print("HTTP Server is running...")
