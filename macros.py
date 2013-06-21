#!/usr/bin/python

import AirCon
import logging
import HueBridge
import SystemStatus
from datetime import datetime

commands = {
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

groups = {
    "1": {"name": "Front Hall", "lightsOn": [7], "command": {"on": True, "bri": 254, "ct": 369}},
    "2": {"name": "Living Room (Overhead)", "lightsOn": [1, 2], "command": {"on": True, "bri": 254, "ct": 369}},
    "3": {"name": "Living Room (Ikea)", "lightsOn": [8, 9, 10], "command": {"on": True, "bri": 254, "ct": 369}},
    "4": {"name": "Kitchen", "lightsOn": [4], "command": {"on": True, "bri": 254, "ct": 369}},
    "5": {"name": "Bedroom (Overhead)", "lightsOn": [5, 6], "command": {"on": True, "bri": 254, "ct": 369}},
    "6": {"name": "Bed Side Lamp", "lightsOn": [3], "command": {"on": True, "bri": 254, "ct": 369}},
    "7": {"name": "Bed Time", "lightsOn": [3], "lightsOff": [1, 2, 4, 5, 6, 7, 8, 9, 10], "command": {"on": True, "bri": 200, "ct": 369}},
    "8": {"name": "Living Room Air Conditioner", "ac": "AC-LR"},
    "9": {"name": "Bedroom Air Conditioner", "ac": "AC-BED"},
    "H": {"name": "Home", "lightsOn": [1, 2, 4], "command": {"on": True, "bri": 254, "ct": 369}},
    "GV": {"name": "GVoice Message", "lightsOn": [9], "command": {"on": True, "bri": 100, "xy": [0.2591, 0.0916]}}
}


def execute(key, modifier):
    global commands, groups

    logging.info("Execute Macro: " + str(key) + " [" + str(modifier) + "]\r")
    if key == "0":
        HueBridge.sendCommandToGroup(0, commands.get("Off"))
        AirCon.turnOff("AC-LR")
        AirCon.turnOff("AC-BED")
        SystemStatus.setAway(True)
    else:
        SystemStatus.setAway(False)
        if key == "H":
            lightSettings = groups.get("H")
            HueBridge.sendCommand(lightSettings.get("lightsOn"), lightSettings.get("command"))
            AirCon.autoOn("AC-LR")
            if datetime.now().hour > 21:
                AirCon.autoOn("AC-BED")
        elif key == "8" or key == "9":
            if key == "8":
                AirCon.controller("AC-LR", modifier)
            elif key == "9":
                AirCon.controller("AC-BED", modifier)
        else:
            lightSettings = groups.get(key)
            if lightSettings is not None:
                lightOn = lightSettings.get("lightsOn")
                lightOff = lightSettings.get("lightsOff")
                if modifier == "UP" or modifier == "DOWN":
                    dimQty = 12
                    curBri = HueBridge.getBrightness(lightOn[0])
                    if modifier == "UP" and curBri <= (254 - dimQty):
                        lightCommand = {"bri": curBri + dimQty}
                    elif modifier == "DOWN" and curBri > dimQty:
                        lightCommand = {"bri": curBri - dimQty}
                    else:
                        lightCommand = {"bri": curBri}
                elif modifier is not None:
                    lightCommand = commands.get(modifier)
                else:
                    lightCommand = lightSettings.get("command")
                if lightOff:
                    HueBridge.turnLightsOff(lightOff)
                if lightOn > 0:
                    HueBridge.sendCommand(lightOn, lightCommand)
            else:
                logging.error("Error: Unrecognized keyboard entry\r")
