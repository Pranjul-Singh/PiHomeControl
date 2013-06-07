#!/usr/bin/env python
import phue
import time
import json
import thread
import PiGPIO
import logging
import KeyboardListener
from datetime import datetime

away = False

itachIP = None
hueBridgeIP = None
hueAppID = "9075e416a7d67c2f6c7d9386dff2e591"

isDoorOpen = False
insideTemperature = -1

lightGroup = {
    "1": {"name": "Front Hall", "lightsOn": [7], "command": {"on": True, "bri": 254, "ct": 369}},
    "2": {"name": "Living Room (Overhead)", "lightsOn": [1, 2], "command": {"on": True, "bri": 254, "ct": 369}},
    "3": {"name": "Living Room (Ikea)", "lightsOn": [8, 9, 10], "command": {"on": True, "bri": 254, "ct": 369}},
    "4": {"name": "Kitchen", "lightsOn": [4], "command": {"on": True, "bri": 254, "ct": 369}},
    "5": {"name": "Bedroom (Overhead)", "lightsOn": [5, 6], "command": {"on": True, "bri": 254, "ct": 369}},
    "6": {"name": "Bed Side Lamp", "lightsOn": [3], "command": {"on": True, "bri": 254, "ct": 369}},
    "7": {"name": "Bed Time", "lightsOn": [3], "lightsOff": [1, 2, 4, 5, 6, 7, 8, 9, 10], "command": {"on": True, "bri": 200, "ct": 369}},
    "8": {"name": "AC-LR", "command": {"on": True, "bri": 254, "ct": 369}},
    "9": {"name": "AC-BED", "command": {"on": True, "bri": 254, "ct": 369}},
    "H": {"name": "Home", "lightsOn": [1, 2, 4], "command": {"on": True, "bri": 254, "ct": 369}}
}

keyModifier = {
    "\t": "Off",
    "/": "VirginBlue",
    "*": "NightRed",
    "\x7f": "DimWhite",
    ".": "Energize"
}

lightCommands = {
    "Default": {"on": True, "bri": 254, "ct": 369},
    "Off": {"on": False},
    "Relax": {"on": True, "bri": 144, "ct": 469},
    "Concentrate": {"on": True, "bri": 219, "ct": 233},
    "Energize": {"on": True, "bri": 203, "ct": 156},
    "Reading": {"on": True, "bri": 240, "ct": 346},
    "DimWhite": {"on": True, "bri": 64, "ct": 369},
    "VirginBlue": {"on": True, "bri": 100, "xy": [0.2591, 0.0916]},
    "NightRed": {"on": True, "bri": 10, "xy": [0.674, 0.322]}
}

acSettings = {
    "DefaultTemp": 69,
    "InsideThreshold": 72,
    "OutsideThreshold": 72
}

acStatus = {}

itachDevice = {
    "AC-LR": {
        "On": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,61,21,3799",
        "Off": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,3799",
        "66": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,21,21,61,21,61,21,61,21,21,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,3799",
        "67": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,3799",
        "68": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,61,21,3799",
        "69": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,61,21,21,21,3799",
        "70": "sendir,1:3,1,37878,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,61,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,61,21,61,21,3787",
        "71": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,3799",
        "72": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,61,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,61,21,3799"
    },
    "AC-BED": {
        "On": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,61,21,3799",
        "Off": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,3799",
        "66": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,21,21,61,21,61,21,61,21,21,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,3799",
        "67": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,3799",
        "68": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,61,21,3799",
        "69": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,61,21,21,21,3799",
        "70": "sendir,1:2,1,37878,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,61,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,61,21,61,21,3787",
        "71": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,3799",
        "72": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,61,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,61,21,3799"
    }
}


_tMonitorLoop = False


def startMonitor():
    global _tMonitorLoop, isDoorOpen
    if _tMonitorLoop is True:
        logging.info("System Status Monitor Already Running")
    else:
        _tMonitorLoop = True
        logger = logging.getLogger('')
        thread.start_new_thread( _getHubStatus, (logger,))
    thread.start_new_thread( _watchDoor, (logger,))


def stopMonitor():
    global _tMonitorLoop
    _tMonitorLoop = False


def _getHubStatus(logger):
    global hueBridgeIP, hueAppID, _tMonitorLoop, acStatus, away
    global itachIP, hueBridgeIP, isDoorOpen, insideTemperature

    logger.info("Starting system status monitor.\r")

    bridge = phue.Bridge(ip=hueBridgeIP, username=hueAppID)

    while _tMonitorLoop:
        data = bridge.get_api()
        data["itachIP"] = itachIP
        data["hueBridgeIP"] = hueBridgeIP
        data["away"] = str(away)
        data["airConditioners"] = acStatus
        data["isDoorOpen"] = isDoorOpen
        data["insideTemperature"] = insideTemperature
        data["updatedAt"] = str(datetime.now())
        data = json.dumps(data)
        with open("status.json", "w") as text_file:
            text_file.write(data)
        time.sleep(10)


def startAway():
    global away
    if away is True:
        logging.info("[AWAY] Already Activated.")
    else:
        logging.info("[AWAY] Activated.")
        away = True
        logger = logging.getLogger('')
        # thread.start_new_thread( _listenForDoor, (logger,))


def stopAway():
    logging.info("[AWAY] Deactivated: Keyboard")
    global away
    away = False


def _watchDoor(logger):
    global isDoorOpen, away

    while True:
        newDoorStatus = PiGPIO.isDoorOpen()
        if newDoorStatus is not isDoorOpen:
            isDoorOpen = newDoorStatus
            if isDoorOpen is True:
                logger.info("Door opened.")
                if away:
                    KeyboardListener.executeMacro("H")
            else:
                logger.info("Door closed.")
        time.sleep(0.5)
