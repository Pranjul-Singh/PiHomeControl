#!/usr/bin/env python

import os
import logging
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


#Create custom HTTPRequestHandler class
class HuePiRequestHandler(BaseHTTPRequestHandler):
    # handle POST command
    def do_POST(self):
        pass

    #handle GET command
    def do_GET(self):
        rootdir = './'  # file location
        try:
            if self.path == "/":
                pass
            elif self.path == "/status":
                pass
            else:
                #open requested file
                f = open(rootdir + self.path)

                #send code 200 response
                self.send_response(200)

                #send header first
                if self.path.endswith(".html"):
                    self.send_header('Content-type', 'text/plain')
                elif self.path.endswith(".js"):
                    pass
                elif self.path.endswith(".css"):
                    pass
                else:
                    pass
                self.end_headers()

                #send file content to client
                self.wfile.write(f.read())
                f.close()
                return

        except IOError:
            self.send_error(404, 'File not found')
        except:
            self.send_error(500, 'Server error')

def run():
    logging.info("Starting HTTP Server...")
    #ip and port of servr
    server_address = ('', 8090)
    httpd = HTTPServer(server_address, HuePiRequestHandler)
    httpd.serve_forever()
    logging.info("HTTP Server is running...")
