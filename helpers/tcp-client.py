#!/usr/bin/python           # This is client.py file

import socket
import macros              # Import socket module

s = socket.socket()         # Create a socket object
ip = "192.168.1.150"        # Get local machine name
port = 4998                 # Reserve a port for your service.



s.connect((ip, port))
s.settimeout(3)
s.send(macros.airCon1.get("69") + "\r")
try:
  print s.recv(1024)
except socket.timeout:
  print "1"
except:
  print "2"
# expected back: completeir,1:3,1
s.close
