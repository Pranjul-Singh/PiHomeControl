#!/usr/bin/python

import Speech
import logging
import HarmonyHub
import HTTPServer
import UDPListener
import SystemStatus
import KeyboardListener


def main():
    try:
        logLevel = logging.INFO
        logFormat = '%(asctime)s | %(levelname)-7s | %(message)s'
        logFile = '../public_html/huepi.log'
        logging.basicConfig(format=logFormat, filename=logFile, level=logLevel)
        console = logging.StreamHandler()
        console.setLevel(logLevel)
        console.setFormatter(logging.Formatter(logFormat))
        logging.getLogger('').addHandler(console)
        print "Homemade Pi"
        logging.info("App Start")

        logging.info("Searching local network for Global Cache iTach...")
        SystemStatus.itachIP = UDPListener.search("239.255.250.250", 9131,
            ["AMXB<-UUID=GlobalCache_", "<-Model=iTachIP2IR>", "<-Status=Ready>"])
        #SystemStatus.itachIP = "192.168.1.150"
        logging.info("iTach IP: [" + str(SystemStatus.itachIP) + "]")

        logging.info("Searching local network for Philips Hue Bridge...")
        SystemStatus.hueBridgeIP = UDPListener.search("239.255.255.250", 1900,
            ["NOTIFY * HTTP/1.1", ":80/description.xml"])
        #SystemStatus.hueBridgeIP = "192.168.1.17"
        logging.info("Hue Bridge IP: [" + str(SystemStatus.hueBridgeIP) + "]")

        logging.info("Searching local network for HarmonyHub...")
        SystemStatus.harmonyHub = HarmonyHub.findHub()
        try:
            logging.info("Harmony Hub: [" + str(SystemStatus.harmonyHub["ip"]) + "]")
        except:
            logging.info("Harmony Hub: Not Found")

        SystemStatus.start()

        # HTTPServer.start()

        logging.info("Ready.")
        Speech.ready()

        KeyboardListener.listen()

        logging.info("Exiting.")
        SystemStatus.stop()

    except Exception, e:
        logging.error("app::main Error Occured - Exiting: " + str(e))
    finally:
        logging.info("Exited.")


if __name__ == "__main__":
    main()
