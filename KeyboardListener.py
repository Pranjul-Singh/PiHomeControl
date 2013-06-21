#!/usr/bin/python

import macros
import logging
import SystemStatus
from getch import GetCh
from datetime import datetime, timedelta

keyModifier = {
    "\t": "Off",
    "/": "VirginBlue",
    "*": "NightRed",
    "\x7f": "DimWhite",
    ".": "Energize",
    "+": "UP",
    "-": "DOWN"
}


def listen():
    global keyModifier

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
            logging.info("User Interupt (Q)\r")
        elif keyModifier.get(charInput) is not None:
            modifier = keyModifier.get(charInput)
            modTimer = datetime.now()
        else:
            if charInput == "\r":
                charInput = "H"
                modifier = None
                SystemStatus.setAway(False)
            elif charInput == "0":
                modifier = None
            macros.execute(charInput, modifier)
            modifier = None
            modTimer = datetime.min
