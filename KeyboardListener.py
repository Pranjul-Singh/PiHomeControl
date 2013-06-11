#!/usr/bin/python

import config
import logging
import HueBridge
import AirCon
from getch import GetCh
from datetime import datetime, timedelta


def listen():
    runLoop = True
    modifier = None
    modTimer = datetime.min

    while runLoop:
        charInput = GetCh()
        if modTimer + timedelta(seconds=4) < datetime.now():
            modifier = None
            modTimer = datetime.min
        if charInput == "q":
            runLoop = False
            logging.info("User Interupt (Q)")
        elif config.keyModifier.get(charInput) is not None:
            modifier = config.keyModifier.get(charInput)
            modTimer = datetime.now()
        else:
            if charInput == "\r":
                charInput = "H"
                modifier = None
                config.stopAway()
            elif charInput == "0":
                modifier = None
                config.startAway()
            else:
                config.stopAway()
            executeMacro(charInput, modifier)
            modifier = None
            modTimer = datetime.min


def executeMacro(key, modifier):
    logging.info("KeyPress: " + str(key) + " [" + str(modifier) + "]")
    if key == "0":
        HueBridge.sendCommandToGroup(0, config.lightCommands.get("Off"))
        AirCon.turnOff("AC-LR")
        AirCon.turnOff("AC-BED")
    elif key == "H":
        lightSettings = config.lightGroup.get("H")
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
        lightSettings = config.lightGroup.get(key)
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
                lightCommand = config.lightCommands.get(modifier)
            else:
                lightCommand = lightSettings.get("command")
            if lightOff:
                HueBridge.turnLightsOff(lightOff)
            if lightOn > 0:
                HueBridge.sendCommand(lightOn, lightCommand)
        else:
            logging.error("Error: Unrecognized keyboard entry")
