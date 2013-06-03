import json
import socket
import macros
import httplib
import logging


def turnAirConOn(ip_address):
    try:
        conn = httplib.HTTPConnection("api.wunderground.com")
        conn.request("GET", "/api/key/conditions/q/40.69748809317884,-73.98093841395088.json")
        r1 = conn.getresponse()
        w = json.loads(r1.read())
        conn.close()
        outside_temp = int(w.get("current_observation").get("temp_f"))
        if outside_temp > 74:
            s = socket.socket()
            port = 4998
            s.settimeout(5)
            s.connect((ip_address, port))
            s.send(macros.airCon1["on"] + "\r")
            response = s.recv(1024)
            s.send(macros.airCon1["69"] + "\r")
            response = s.recv(1024)
            s.close()
            logging.info("-H- [None] [AC1] {'on': True, 'temp': 69, 'outside': %s}", str(outside_temp))
    except socket.timeout:
        pass
    except:
        logging.error("AirCon::turnAirConOn - Unknown Error")
    return


def turnAirConOff(ip_address):
    try:
        s = socket.socket()
        port = 4998
        s.settimeout(5)
        s.connect((ip_address, port))
        s.send(macros.airCon1["off"] + "\r")
        response = s.recv(1024)
        logging.info("-0- [None] [AC1] {'on': False}")
        s.send(macros.airCon2["off"] + "\r")
        response = s.recv(1024)
        logging.info("-0- [None] [AC2] {'on': False}")
        s.close()
    except socket.timeout:
        pass
    except:
        logging.error("AirCon::turnAirConOff - Unknown Error")
    return
