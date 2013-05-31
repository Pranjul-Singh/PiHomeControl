#!/usr/bin/python

from FindHue import FindHue
from FindiTach import FindiTach
from getch import GetCh
from datetime import datetime, timedelta
import macros
import logging
import thread
import AirCon


def executeMacro(hub, key, modifier):
    log_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = "-" + key + "- [" + str(modifier) + "] "

    if key == "0":
        command = {"on": False}
        log = log + "[G0] " + str(command)
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
    print "Searching local network for Global Cache iTach..."
    logging.info("Searching local network for Global Cache iTach...")
    itach_ip = FindiTach().search()
    if itach_ip is None:
        print "iTach not found."
        logging.info("iTach not found.")
    else:
        print "Bridge found: %s" % str(itach_ip)
        logging.info("iTach found: %s" % str(itach_ip))
        logging.info("Success.")

    print "Searching local network for Philips Hue Bridge..."
    logging.info("Searching local network for Philips Hue Bridge...")
    hub = FindHue().search()
    if hub is None:
        print "Hue bridge not found."
        logging.info("Hue bridge not found.")
    else:
        print "Bridge found: %s" % str(hub.ip)
        print "Started: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print "Ready."
        runLoop = True
        logging.info("Hue bridge found: %s" % str(hub.ip))
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
            elif charInput == "1" \
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
            elif charInput == "0":
                # All Off
                thread.start_new_thread(AirCon.turnAirConOff, (itach_ip,))
                executeMacro(hub, "0", None)
                modifier = None
                modTimer = datetime.min
            elif charInput == "\r":
                # Enter Key
                thread.start_new_thread(AirCon.turnAirConOn, (itach_ip,))
                executeMacro(hub, "H", None)
                modifier = None
                modTimer = datetime.min
        except Exception, e:
            logging.error("main::runLoop")
            logging.error(str(e))
            print "Exception"
            print e

if __name__ == "__main__":
    main()
