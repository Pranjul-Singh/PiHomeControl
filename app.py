#!/usr/bin/python

import config
import PiGPIO
import logging
import UDPListener
import KeyboardListener


def main():
    logLevel = logging.INFO
    logFormat = '%(asctime)s | %(levelname)-7s | %(message)s'
    logFile = './huepi.log'
    logging.basicConfig(format=logFormat, filename=logFile, level=logLevel)
    console = logging.StreamHandler()
    console.setLevel(logLevel)
    console.setFormatter(logging.Formatter(logFormat))
    logging.getLogger('').addHandler(console)
    print "Homemade Pi"
    logging.info("App Start")

    logging.info("Searching local network for Global Cache iTach...")
    config.itachIP = UDPListener.search("239.255.250.250", 9131,
        ["AMXB<-UUID=GlobalCache_", "<-Model=iTachIP2IR>", "<-Status=Ready>"])
    logging.info("iTach IP: [" + str(config.itachIP) + "]")

    logging.info("Searching local network for Philips Hue Bridge...")
    config.hueBridgeIP = UDPListener.search("239.255.255.250", 1900,
        ["NOTIFY * HTTP/1.1", ":80/description.xml"])
    logging.info("Hue Bridge IP: [" + str(config.hueBridgeIP) + "]")

    #config.startMonitor()
    #PiGPIO.startDoorMonitor()

    logging.info("Ready.")

    KeyboardListener.listen()

    logging.info("Exiting.")

if __name__ == "__main__":
    main()
