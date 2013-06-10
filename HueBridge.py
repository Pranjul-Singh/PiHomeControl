#!/usr/bin/python

import config
import logging
import phue
import json

global _bridge
_bridge = None


def _checkBridge():
    global _bridge
    if _bridge is None and config.hueBridgeIP is not None:
            _bridge = phue.Bridge(ip=config.hueBridgeIP, username=config.hueAppID)


def sendCommand(lights, command):
    global _bridge
    logging.info(str(lights) + " -> " + str(command))
    try:
        _checkBridge()
        if _bridge is None:
            logging.error("  HueBridge::sendCommand: No Bridge Available")
        else:
            logging.info(" <- " + json.dumps(_bridge.set_light(lights, command)))
    except Exception, e:
        logging.error("  HueBridge::sendCommand: " + str(e))


def sendCommandToGroup(group, command):
    global _bridge
    logging.info("[G" + str(group) + "] -> " + str(command))
    try:
        _checkBridge()
        if _bridge is None:
            logging.error("  HueBridge::sendCommand: No Bridge Available")
        else:
            logging.info(" <- " + json.dumps(_bridge.set_group(group, command)))
    except Exception, e:
        logging.error("  HueBridge::sendCommandToGroup: " + str(e))


def turnLightsOff(lights):
    global _bridge
    logging.info(str(lights) + " -> " + str(config.lightCommands.get("Off")))
    try:
        _checkBridge()
        if _bridge is None:
            logging.error("  HueBridge::sendCommand: No Bridge Available")
        else:
            logging.info(" <- " + json.dumps(_bridge.set_light(lights, config.lightCommands.get("Off"))))
    except Exception, e:
        logging.error("  HueBridge::turnLightsOff: " + str(e))


## TODO Finish up this section!!!
def adjustBrightness(lights, direction):
    global _bridge
    logging.info(str(lights) + " -> Brightness: " + direction)
    try:
        _checkBridge()
        if _bridge is None:
            logging.error("  HueBridge::sendCommand: No Bridge Available")
        else:
            for light in lights:
                try:
                    currentBrightness = config.hueHubStatus.get("lights").get(light).get("status").get("bri")
                    if direction == "UP" and currentBrightness <= 249:
                        currentBrightness += 5
                        logging.info("New brightness: " + str(currentBrightness))
                    elif direction == "DOWN" and currentBrightness >= 6:
                        currentBrightness -= 5
                        logging.info("New brightness: " + str(currentBrightness))
                    else:
                        logging.warn("  HueBridge::adjustBrightness: No direction specified.")
                except:
                    logging.warn("  HueBridge::adjustBrightness: Couldn't get current light brightness for light: " + str(light))
    except Exception, e:
        logging.error("  HueBridge::adjustBrightness: " + str(e))

