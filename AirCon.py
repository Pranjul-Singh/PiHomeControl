import json
import PiGPIO
import socket
import config
import httplib
import logging


#def turnAirConOn(device, ext_temp, set_temp):

def _outsideTemp():
    try:
        conn = httplib.HTTPConnection("api.wunderground.com")
        conn.request("GET", "/api/KEY/conditions/q/40.69748809317884,-73.98093841395088.json")
        r1 = conn.getresponse()
        w = json.loads(r1.read())
        conn.close()
        curTemp = int(w.get("current_observation").get("temp_f"))
        return curTemp
    except Exception, e:
        pass
        logging.error("Unable to get outdoor temperature. " + str(e))
        return -1


def _sendCommand(command):
    try:
        if config.itachIP is None:
            logging.error("  Error - AirCon::_sendComand: iTach Bridge Not Found")
        else:
            s = socket.socket()
            port = 4998
            s.settimeout(5)
            s.connect((config.itachIP, port))
            s.send(command + "\r")
            response = s.recv(1024)
            logging.info(" <- " + str(response))
            s.close()
    except Exception, e:
        logging.error("Error sending IR command: " + str(e))


def turnOff(device):
    logging.info("[" + device + "] -> Off")
    deviceCommands = config.itachDevice.get(device)
    if deviceCommands is not None:
        _sendCommand(deviceCommands.get("Off"))
        config.acStatus[device] = {"Running": False, "Temperature": config.acSettings.get("DefaultTemp")}
    else:
        logging.info("  Error - AirCon::turnOff: Device Not Found")


def turnOn(device):
    logging.info("[" + device + "] -> On")
    deviceCommands = config.itachDevice.get(device)
    if deviceCommands is not None:
        _sendCommand(deviceCommands.get("On"))
        _sendCommand(str(config.acSettings.get("DefaultTemp")))
        config.acStatus[device] = {"Running": True, "Temperature": config.acSettings.get("DefaultTemp")}
    else:
        logging.info("  Error - AirCon::turnOff: Device Not Found")


def autoOn(device):
    insideTemp = PiGPIO.insideTemperature()
    insideThresh = config.acSettings.get("InsideThreshold")
    insideExceeds = insideTemp > insideThresh
    outsideTemp = _outsideTemp()
    outsideThresh = config.acSettings.get("OutsideThreshold")
    outsideExceeds = outsideTemp > outsideThresh
    logging.info("[" + device + "] -> Auto")
    logging.info(" Inside:  " + str(insideTemp) + " | " + str(insideThresh))
    logging.info(" Outside: " + str(outsideTemp) + " | " + str(outsideThresh))
    if insideExceeds or outsideExceeds:
        deviceCommands = config.itachDevice.get(device)
        if deviceCommands is not None:
            _sendCommand(deviceCommands.get("On"))
            _sendCommand(str(config.acSettings.get("DefaultTemp")))
            config.acStatus[device] = {"Running": True, "Temperature": config.acSettings.get("DefaultTemp")}


def increaseTemp(device):
    status = config.acStatus.get(device)
    if status is not None:
        if status.get("Running") is True:
            newTemp = status.get("Temperature") + 1
            command = config.itachDevice.get(device).get(str(newTemp))
            if command is not None:
                _sendCommand(command)
                config.acStatus[device]["Temperature"] = newTemp
                logging.info("[" + device + "] -> {" + str(newTemp) + "}")
                logging.info(config.acStatus[device]["Temperature"])


def decreaseTemp(device):
    status = config.acStatus.get(device)
    if status is not None:
        if status.get("Running") is True:
            newTemp = status.get("Temperature") - 1
            command = config.itachDevice.get(device).get(str(newTemp))
            if command is not None:
                _sendCommand(command)
                config.acStatus[device]["Temperature"] = newTemp
                logging.info("[" + device + "] -> {" + str(newTemp) + "}")
                logging.info(config.acStatus[device]["Temperature"])
