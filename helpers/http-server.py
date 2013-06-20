#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os

#Create custom HTTPRequestHandler class
class HuePiRequestHandler(BaseHTTPRequestHandler):
    # handle POST command
    def do_POST(self):
        pass

    #handle GET command
    def do_GET(self):
        rootdir = './' #file location
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
                    self.send_header('Content-type','text/plain')
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
    print('http server is starting...')

    #ip and port of servr
    #by default http server port is 80
    server_address = ('', 8090)
    httpd = HTTPServer(server_address, HuePiRequestHandler)
    print('http server is running...')
    httpd.serve_forever()
    print('http server is...')
    
if __name__ == '__main__':
    run()