#!/usr/bin/python

from findhub import FindHub
from getch import GetCh
from datetime import datetime, timedelta
import macros
import logging


# http://www.cl.cam.ac.uk/projects/raspberrypi/tutorials/turing-machine/two.html


def executeMacro(hub, key, modifier):
    log_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = "-" + key + "- [" + str(modifier) + "] "

    if key == "0":
        if modifier == "OFF":
            command = macros.colors["Default"]
        elif modifier == "ALT1":
            command = macros.colors["VirginBlue"]
        elif modifier == "ALT2":
            command = macros.colors["NightRed"]
        elif modifier == "ALT3":
            command = macros.colors["DimWhite"]
        elif modifier == "ALT4":
            command = macros.colors["Energize"]
        else:
            command = {"on": False}
        log = log + "G(0) " + str(command)
        hub.set_group(0, command)
    else:
        try:
            macro = macros.macros[key]
            if modifier == "OFF":
                command = {"on": False}
            elif modifier == "ALT1":
                command = macros.colors["VirginBlue"]
            elif modifier == "ALT2":
                command = macros.colors["NightRed"]
            elif modifier == "ALT3":
                command = macros.colors["DimWhite"]
            elif modifier == "ALT4":
                command = macros.colors["Energize"]
            else:
                command = macro["command"]
            log = log + str(macro["lightsOn"]) + " "
            log = log + str(command) + " "
            if macro.get("lightsOff"):
                hub.set_light(macro["lightsOff"], {"on": False})
            if macro.get("lightsOn"):
                hub.set_light(macro["lightsOn"], command)
        except:
            logging.error("executeMacro " + key + " " + modifier)
    print log_date + " " + log
    logging.info(log)
    return


def main():
    logging.basicConfig(format='%(asctime)s %(message)s', filename='./huepi.log', level=logging.INFO)
    logging.info("")
    logging.info("")
    logging.info("**** HuePi - Start")

    runLoop = False
    modifier = None
    modTimer = datetime.min

    print "HuePi"
    print "Searching local network for Philips Hue Bridge..."
    hub = FindHub().search()
    if hub is None:
        print "Bridge not found."
        logging.info("Bridge not found.")
    else:
        print "Bridge found: %s" % str(hub.ip)
        print "Started: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print "Ready."
        runLoop = True
        logging.info("Success.")

    while runLoop:
        try:
            charInput = GetCh()
            if modTimer + timedelta(seconds=3) < datetime.now():
                modifier = None
                modTimer = datetime.min
            if charInput == "q":
                runLoop = False
                logging.info("User Interupt (Q)")
            elif charInput == "0" or charInput == "1" \
                 or charInput == "2" or charInput == "3" \
                 or charInput == "4" or charInput == "5" \
                 or charInput == "6" or charInput == "7" \
                 or charInput == "8" or charInput == "9":
                executeMacro(hub, charInput, modifier)
                modifier = None
                modTimer = datetime.min
            elif charInput == "-":
                print "NYI: Dim Light"
                logging.info("NYI: Dim Light")
            elif charInput == "+":
                print "NYI: Brighten Light"
                logging.info("NYI: Brighten Light")
            elif charInput == "\t":
                # Turn off modifier
                modifier = "OFF"
                modTimer = datetime.now()
            elif charInput == "/":
                # Alternate modifier
                modifier = "ALT1"
                modTimer = datetime.now()
            elif charInput == "*":
                # Alternate modifier2
                modifier = "ALT2"
                modTimer = datetime.now()
            elif charInput == "\x7f":
                # Alternate modifier3
                modifier = "ALT3"
                modTimer = datetime.now()
            elif charInput == ".":
                # Alternate modifier4
                modifier = "ALT4"
                modTimer = datetime.now()
            elif charInput == "\r":
                # Enter Key
                executeMacro(hub, "H", None)
        except Exception, e:
            logging.error("main::runLoop")
            logging.error(str(e))
            print "Exception"
            print e

if __name__ == "__main__":
    main()
