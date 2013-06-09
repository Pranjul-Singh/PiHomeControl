import json
import time
import socket
import config
import logging


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
        logging.error("Error sending IR command: " + command)
        logging.error("Error: " + str(e))


def turnOff(device):
    logging.info("[" + device + "] -> Off")
    deviceCommands = config.itachDevice.get(device)
    if deviceCommands is not None:
        _sendCommand(deviceCommands.get("Off"))
        config.acStatus[device] = {"Running": False, "Temperature": config.acSettings.get("DefaultTemp")}
    else:
        logging.info("  Error - AirCon::turnOff: Device Not Found")


def turnOn(device):
    deviceCommands = config.itachDevice.get(device)
    if deviceCommands is not None:
        logging.info("[" + device + "] -> On")
        _sendCommand(deviceCommands.get("On"))
        defaultTemp = config.acSettings.get("DefaultTemp")
        logging.info("[" + device + "] -> " + str(defaultTemp))
        _sendCommand(deviceCommands.get(str(defaultTemp)))
        config.acStatus[device] = {"Running": True, "Temperature": defaultTemp}
    else:
        logging.info("  Error - AirCon::turnOff: Device Not Found")


def autoOn(device):
    insideTemp = config.insideTemperature()
    insideThresh = config.acSettings.get("InsideThreshold")
    insideExceeds = insideTemp > insideThresh
    outsideTemp = config.outsideTemperature(False)
    outsideThresh = config.acSettings.get("OutsideThreshold")
    outsideExceeds = outsideTemp > outsideThresh
    logging.info("[" + device + "] -> Auto")
    logging.info(" Inside:  " + str(insideTemp) + " | " + str(insideThresh))
    logging.info(" Outside: " + str(outsideTemp) + " | " + str(outsideThresh))
    if insideExceeds or outsideExceeds:
        deviceCommands = config.itachDevice.get(device)
        if deviceCommands is not None:
            logging.info("[" + device + "] -> On")
            _sendCommand(deviceCommands.get("On"))
            defaultTemp = config.acSettings.get("DefaultTemp")
            logging.info("[" + device + "] -> " + str(defaultTemp))
            _sendCommand(deviceCommands.get(str(defaultTemp)))
            config.acStatus[device] = {"Running": True, "Temperature": defaultTemp}


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
