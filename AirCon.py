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


def controller(device, command):
    logging.debug("AC Controller: [" + device + "] -> " + str(command))
    if command == "Off":
        turnOff(device)
    elif command == "AC-UP" and config.acStatus[device] is not "OFF":
        increaseTemp(device)
    elif command == "AC-DOWN" and config.acStatus[device] is not "OFF":
        decreaseTemp(device)
    elif config.acStatus[device]["mode"] == "OFF":
        turnOn(device)        
    # elif config.acStatus[device]["mode"] == "OFF" or config.acStatus[device]["mode"] == "DEH":
    #     turnOn(device)
    # elif config.acStatus[device]["mode"] == "ON":
    #     turnOnFan(device)
    # elif config.acStatus[device]["mode"] == "FAN":
    #     turnOnDeh(device)


def turnOff(device):
    logging.info("[" + device + "] -> Off")
    deviceCommands = config.itachDevice.get(device)
    if deviceCommands is not None:
        _sendCommand(deviceCommands.get("Off"))
        config.acStatus[device]["mode"] = "OFF"
        config.acStatus[device]["temperature"] = -1
        config.acStatus[device]["fan"] = "OFF"
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
        config.acStatus[device]["mode"] = "ON"
        config.acStatus[device]["temperature"] = defaultTemp
        config.acStatus[device]["fan"] = "OFF"
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
            config.acStatus[device]["mode"] = "ON"
            config.acStatus[device]["temperature"] = defaultTemp
            config.acStatus[device]["fan"] = "OFF"


# def turnOnFan(device):
#     deviceCommands = config.itachDevice.get(device)
#     if deviceCommands is not None:
#         logging.info("[" + device + "] -> Fan On")
#         _sendCommand(deviceCommands.get("FanOn"))
#         config.acStatus[device]["mode"] = "FAN"
#         config.acStatus[device]["temperature"] = -1
#         config.acStatus[device]["fan"] = "MEDIUM"
#     else:
#         logging.info("  Error - AirCon::turnOnFan: Device Not Found")



# def turnOnDeh(device):
#     deviceCommands = config.itachDevice.get(device)
#     if deviceCommands is not None:
#         logging.info("[" + device + "] -> Dehumidifier On")
#         _sendCommand(deviceCommands.get("DehumidifierOn"))
#         config.acStatus[device]["mode"] = "DEH"
#         config.acStatus[device]["temperature"] = 70
#         config.acStatus[device]["fan"] = "OFF"
#     else:
#         logging.info("  Error - AirCon::turnOnDeh: Device Not Found")


def increaseTemp(device):
    status = config.acStatus.get(device)
    if status is not None:
        if status.get("mode") is "ON":
            newTemp = status.get("temperature") + 1
            command = config.itachDevice.get(device).get(str(newTemp))
            if command is not None:
                _sendCommand(command)
                config.acStatus[device]["temperature"] = newTemp
                logging.info("[" + device + "] -> {" + str(newTemp) + "}")
                

def decreaseTemp(device):
    status = config.acStatus.get(device)
    if status is not None:
        if status.get("mode") is "ON":
            newTemp = status.get("temperature") - 1
            command = config.itachDevice.get(device).get(str(newTemp))
            if command is not None:
                _sendCommand(command)
                config.acStatus[device]["temperature"] = newTemp
                logging.info("[" + device + "] -> {" + str(newTemp) + "}")
                