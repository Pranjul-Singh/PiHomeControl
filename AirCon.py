import socket
import SystemStatus
import logging

_defaultTemp = 71
_insideThresh = 73
_outsideThresh = 75

_itachDevice = {
    "AC-LR": {
        "On": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,61,21,3799",
        "Off": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,3799",
        "66": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,21,21,61,21,61,21,61,21,21,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,3799",
        "67": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,3799",
        "68": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,61,21,3799",
        "69": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,61,21,21,21,3799",
        "70": "sendir,1:2,1,37878,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,61,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,61,21,61,21,3787",
        "71": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,3799",
        "72": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,61,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,61,21,3799",
        "FanOn": "version",
        "DehumidifierOn": "version"
    },
    "AC-BED": {
        "On": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,61,21,3799",
        "Off": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,3799",
        "66": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,21,21,61,21,61,21,61,21,21,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,3799",
        "67": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,3799",
        "68": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,61,21,3799",
        "69": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,61,21,21,21,3799",
        "70": "sendir,1:3,1,37878,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,61,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,61,21,61,21,3787",
        "71": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,3799",
        "72": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,61,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,61,21,3799",
        "FanOn": "version",
        "DehumidifierOn": "version"
    }
}


def _sendCommand(command):
    try:
        if SystemStatus.itachIP is None:
            logging.error("  Error - AirCon::_sendComand: iTach Bridge Not Found")
        else:
            s = socket.socket()
            port = 4998
            s.settimeout(5)
            s.connect((SystemStatus.itachIP, port))
            s.send(command + "\r")
            response = s.recv(1024)
            logging.info(" <- " + str(response))
            s.close()
    except Exception, e:
        logging.error("Error sending IR command: " + command)
        logging.error("Error: " + str(e))


def controller(device, command):
    status = SystemStatus.get().get("airConditioners").get(device)
    logging.debug("AC Controller: [" + device + "] -> " + str(command))
    if command == "Off":
        turnOff(device)
    elif command == "UP" and status.get("mode") is not "OFF":
        increaseTemp(device)
    elif command == "DOWN" and status.get("mode") is not "OFF":
        decreaseTemp(device)
    elif status.get("mode") == "OFF":
        turnOn(device)


def turnOff(device):
    global _itachDevice

    status = SystemStatus.get().get("airConditioners").get(device)
    logging.info("[" + device + "] -> Off")
    deviceCommands = _itachDevice.get(device)
    if deviceCommands is not None:
        _sendCommand(deviceCommands.get("Off"))
        status["mode"] = "OFF"
        status["temperature"] = -1
        status["fan"] = "OFF"
    else:
        logging.info("  Error - AirCon::turnOff: Device Not Found")


def turnOn(device):
    global _itachDevice, _defaultTemp

    status = SystemStatus.get().get("airConditioners").get(device)
    logging.info("[" + device + "] -> On")
    deviceCommands = _itachDevice.get(device)
    if deviceCommands is not None:
        _sendCommand(deviceCommands.get("On"))
        logging.info("[" + device + "] -> " + str(_defaultTemp))
        _sendCommand(deviceCommands.get(str(_defaultTemp)))
        status["mode"] = "ON"
        status["temperature"] = _defaultTemp
        status["fan"] = "OFF"
    else:
        logging.info("  Error - AirCon::turnOff: Device Not Found")


def autoOn(device):
    global _itachDevice, _defaultTemp, _insideThresh, _outsideThresh

    insideTemp = SystemStatus.get().get("insideTemperature")
    insideExceeds = insideTemp > _insideThresh
    outsideTemp = SystemStatus.get().get("outsideTemperature")
    outsideExceeds = outsideTemp > _outsideThresh
    logging.info("[" + device + "] -> Auto")
    logging.info(" Inside:  " + str(insideTemp) + " | " + str(_insideThresh))
    logging.info(" Outside: " + str(outsideTemp) + " | " + str(_outsideThresh))
    if insideExceeds or outsideExceeds:
        turnOn(device)


def decreaseTemp(device):
    _changeTemp(device, "DOWN")


def increaseTemp(device):
    _changeTemp(device, "UP")


def _changeTemp(device, dir):
    status = SystemStatus.get().get("airConditioners").get(device)
    if status is not None:
        if status.get("mode") is "ON":
            if dir == "UP":
                newTemp = status.get("temperature") + 1
            else:
                newTemp = status.get("temperature") - 1
            command = _itachDevice.get(device).get(str(newTemp))
            if command is not None:
                _sendCommand(command)
                status["temperature"] = newTemp
                logging.info("[" + device + "] -> {" + str(newTemp) + "}")
