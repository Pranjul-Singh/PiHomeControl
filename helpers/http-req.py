#!/usr/bin/python           # This is client.py file

import json
import httplib


conn = httplib.HTTPConnection("api.wunderground.com")
conn.request("GET", "/api/[key]/conditions/q/40.69748809317884,-73.98093841395088.json")
r1 = conn.getresponse()
print r1.status, r1.reason
data1 = r1.read()
print data1
conn.request("GET", "/api/[key]/astronomy/q/40.69748809317884,-73.98093841395088.json")
r2 = conn.getresponse()
print r2.status, r2.reason
data2 = r2.read()
print data2
conn.close()
