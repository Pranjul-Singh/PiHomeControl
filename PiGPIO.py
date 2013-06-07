import os
import glob
import time
import thread
import logging

try:
    import RPi.GPIO as io
    _gpioWorking = True
except:
    _gpioWorking = False
    _loggedOnce = False


def isDoorOpen():
    global _loggedOnce

    if _gpioWorking is True:
        return _isDoorOpenGPIO()
    else:
        if _loggedOnce is False:
            logging.warn("GPIO Door detection not working.\r")
            _loggedOnce = True
        return False


def _isDoorOpenGPIO():
    piDoorPin = 23
    try:
        if io.input(piDoorPin) is True:
            return True
        else:
            return False
    except:
        logging.error("Unable to obtain door status\r")
        return False


def insideTemperature():
    return -1
