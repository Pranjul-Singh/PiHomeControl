import os
import glob
import time
import thread
import logging

_gpioReady = False

try:
    # import RPi.GPIO as io
    # _gpioReady = True
    _gpioReady = False
except ImportError, e:
    _gpioReady = False


_piDoorPin = 23
isDoorOpen = False


def _runDoorLoop(logger):
    global isDoorOpen, _gpioReady

    while True:
        try:
            if io.input(_piDoorPin) is True and isDoorOpen is False:
                logger.info("Door opened.\r")
                isDoorOpen = True
            elif io.input(_piDoorPin) is False and isDoorOpen is True:
                logger.info("Door closed.\r")
                isDoorOpen = False
        except Exception, e:
            logger.error("Unable to determine door status: " + str(e) + "\r")
        finally:
            time.sleep(0.5)


def insideTemperature():
    return -1


def startDoorMonitor():
    global isDoorOpen
    logging.info("Starting door monitor.")
    if _gpioReady is True:
        logger = logging.getLogger('')
        thread.start_new_thread( _runDoorLoop, (logger,))
        if isDoorOpen:
            logging.info(" Door open.")
        else:
            logging.info(" Door closed.")
    else:
        logging.error("Failed to start Door Watch: Pi GPIO not ready.")
