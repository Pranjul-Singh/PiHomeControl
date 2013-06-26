#!/usr/bin/env python

import cgi
import json
import macros
import thread
import logging
import SystemStatus
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


#Create custom HTTPRequestHandler class
class HuePiRequestHandler(BaseHTTPRequestHandler):
    def log_message( self, format, *args ):
      pass
      # logging.info("HTTPD: " + str(args) + "\r")

    def get_mime_type(extension):
        # text/css
        # text/html
        # application/javascript
        # image/jpeg,gif,png
        return "text/plain"

    # handle POST command
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}
        try:
            if self.path == "/execute":
                key = postvars.get("key")[0]
                modifier = postvars.get("modifier")[0]
                if modifier == "":
                    modifier = None
                macros.execute(key, modifier)
                response = '{"updated": true}'
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response)
                return
            else:
                self.send_error(404, 'File not found')
        except Exception, e:
            self.send_error(500, str(e))

    #handle GET command
    def do_GET(self):
        # rootdir = './'  # file location
        response_code = 404
        response = ""
        mime_type = ""
        try:
            if self.path == "/kp":
                f = open("keypad.html")
                response = f.read()
                f.close()
                response_code = 200
                mime_type = 'text/html'

            elif self.path == "/status":
                response = json.dumps(SystemStatus.get())
                mime_type = 'application/json'
                response_code = 200

            else:
                response = "Nothing to see here, move along."
                mime_type = "text/plain"

            #send file content to client
            self.send_response(response_code)
            self.send_header('Content-type', mime_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response)
            return
        except IOError:
            self.send_error(404, 'File not found')
        except Exception, e:
            self.send_error(500, str(e))


def start():
    thread.start_new_thread( _run, (logging.getLogger(''),))


def _run(logger):
    try:
        logger.info("Starting HTTP Server...\r")
        server_address = ('', 8090)
        httpd = HTTPServer(server_address, HuePiRequestHandler)
        httpd.serve_forever()
        logger.info("HTTP Server is running...\r")
    except Exception, e:
        logging.error("Unable to start the HTTP Server: " + str(e) + "\r")
