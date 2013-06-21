#!/usr/bin/python

import phue
import json
import macros
import logging
import SystemStatus

_bridge = None


def _checkBridge():
    global _bridge
    if _bridge is None and SystemStatus.hueBridgeIP is not None:
            _bridge = phue.Bridge(ip=SystemStatus.hueBridgeIP, username=SystemStatus.hueAppID)


def sendCommand(lights, command):
    global _bridge
    logging.info(str(lights) + " -> " + str(command) + "\r")
    try:
        _checkBridge()
        if _bridge is None:
            logging.error("  HueBridge::sendCommand: No Bridge Available\r")
        else:
            result = json.dumps(_bridge.set_light(lights, command))
            logging.info(" <- " + result + "\r")
            return result
    except Exception, e:
        logging.error("  HueBridge::sendCommand: " + str(e) + "\r")


def sendCommandToGroup(group, command):
    global _bridge
    logging.info("[G" + str(group) + "] -> " + str(command) + "\r")
    try:
        _checkBridge()
        if _bridge is None:
            logging.error("  HueBridge::sendCommand: No Bridge Available\r")
        else:
            result = json.dumps(_bridge.set_group(group, command))
            logging.info(" <- " + result + "\r")
            return result
    except Exception, e:
        logging.error("  HueBridge::sendCommandToGroup: " + str(e) + "\r")


def turnLightsOff(lights):
    global _bridge
    logging.info(str(lights) + " -> " + str(macros.commands.get("Off")) + "\r")
    try:
        _checkBridge()
        if _bridge is None:
            logging.error("  HueBridge::sendCommand: No Bridge Available\r")
        else:
            result = json.dumps(_bridge.set_light(lights, macros.commands.get("Off")) + "\r")
            logging.info(" <- " + result + "\r")
            return result
    except Exception, e:
        logging.error("  HueBridge::turnLightsOff: " + str(e) + "\r")


def getBrightness(light):
    global _bridge
    try:
        _checkBridge()
        if _bridge is None:
            logging.error("  HueBridge::getBrightness: No Bridge Available\r")
        else:
            return _bridge.get_light(light, "bri")
    except Exception, e:
        logging.error("  HueBridge::getBrightness: " + str(e) + "\r")
