#!/usr/bin/env python
import os
import glob
import phue
import time
import json
import thread
import logging
import httplib
import KeyboardListener
from datetime import datetime, timedelta


# http://pythonhosted.org/RPIO/

startTime = datetime.now()

away = False
awayArmed = datetime.min

itachIP = None
hueBridgeIP = None
hueAppID = "9075e416a7d67c2f6c7d9386dff2e591"

isDoorOpen = False

_outsideTemperature = {"temp": -1, "time": datetime.min}
_tempSensorPath = None

lightGroup = {
    "1": {"name": "Front Hall", "lightsOn": [7], "command": {"on": True, "bri": 254, "ct": 369}},
    "2": {"name": "Living Room (Overhead)", "lightsOn": [1, 2], "command": {"on": True, "bri": 254, "ct": 369}},
    "3": {"name": "Living Room (Ikea)", "lightsOn": [8, 9, 10], "command": {"on": True, "bri": 254, "ct": 369}},
    "4": {"name": "Kitchen", "lightsOn": [4], "command": {"on": True, "bri": 254, "ct": 369}},
    "5": {"name": "Bedroom (Overhead)", "lightsOn": [5, 6], "command": {"on": True, "bri": 254, "ct": 369}},
    "6": {"name": "Bed Side Lamp", "lightsOn": [3], "command": {"on": True, "bri": 254, "ct": 369}},
    "7": {"name": "Bed Time", "lightsOn": [3], "lightsOff": [1, 2, 4, 5, 6, 7, 8, 9, 10], "command": {"on": True, "bri": 200, "ct": 369}},
    "8": {"name": "Living Room Air Conditioner", "ac": "AC-LR"},
    "9": {"name": "Bedroom Air Conditioner", "ac": "AC-BED"},
    "H": {"name": "Home", "lightsOn": [1, 2, 4], "command": {"on": True, "bri": 254, "ct": 369}}
}

keyModifier = {
    "\t": "Off",
    "/": "VirginBlue",
    "*": "NightRed",
    "\x7f": "DimWhite",
    ".": "Energize",
    "+": "UP",
    "-": "DOWN"
}

lightCommands = {
    "Default": {"on": True, "bri": 254, "ct": 369},
    "Off": {"on": False},
    "Relax": {"on": True, "bri": 144, "ct": 469},
    "Concentrate": {"on": True, "bri": 219, "ct": 233},
    "Energize": {"on": True, "bri": 203, "ct": 156},
    "Reading": {"on": True, "bri": 240, "ct": 346},
    "DimWhite": {"on": True, "bri": 64, "ct": 369},
    "VirginBlue": {"on": True, "bri": 100, "xy": [0.2591, 0.0916]},
    "NightRed": {"on": True, "bri": 10, "xy": [0.674, 0.322]}
}

acSettings = {
    "DefaultTemp": 69,
    "InsideThreshold": 72,
    "OutsideThreshold": 72
}

acStatus = {}

itachDevice = {
    "AC-LR": {
        "On": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,61,21,3799",
        "Off": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,3799",
        "66": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,21,21,61,21,61,21,61,21,21,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,3799",
        "67": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,3799",
        "68": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,61,21,3799",
        "69": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,61,21,21,21,3799",
        "70": "sendir,1:3,1,37878,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,61,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,61,21,61,21,3787",
        "71": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,3799",
        "72": "sendir,1:3,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,61,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,61,21,3799",
        "FanOn": "version",
        "DehumidifierOn": "version"
    },
    "AC-BED": {
        "On": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,61,21,3799",
        "Off": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,3799",
        "66": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,21,21,61,21,61,21,61,21,21,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,3799",
        "67": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,3799",
        "68": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,21,21,61,21,3799",
        "69": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,61,21,61,21,21,21,3799",
        "70": "sendir,1:2,1,37878,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,21,21,61,21,61,21,21,21,21,21,61,21,21,21,21,21,61,21,61,21,61,21,3787",
        "71": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,3799",
        "72": "sendir,1:2,1,37993,1,1,319,160,21,61,21,21,21,21,21,21,21,61,21,21,21,21,21,21,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,21,21,61,21,61,21,21,21,61,21,21,21,21,21,61,21,21,21,61,21,21,21,21,21,61,21,3799",
        "FanOn": "version",
        "DehumidifierOn": "version"
    }
}


_tMonitorLoop = False


def doorCallback(gpio_id, val):
    global isDoorOpen, away, lastKeyTime
    if val == 1:
        isDoorOpen = True
        logging.info("Door opened.\r")
        if away is True:
            away = False
            KeyboardListener.executeMacro("H", None)
            logging.info("[AWAY] Deactivated: Door\r")
            ledToggle(False)
    else:
        isDoorOpen = False 
        logging.info("Door closed.\r")


def initAC():
    global acStatus

    acStatus = {
        "AC-BED": {
            "mode": "OFF",
            "temperature": -1,
            "fan": "OFF"
        },
        "AC-LR": {
            "mode": "OFF",
            "temperature": -1,
            "fan": "OFF"
        },
    }


def startMonitor():
    global _tMonitorLoop, isDoorOpen
    if _tMonitorLoop is True:
        logging.warn("System Status Monitor Already Running")
    else:
        ledToggle(False)
        logging.info("Starting system status monitor.")
        _tMonitorLoop = True
        logger = logging.getLogger('')
        initTempSensor()
        thread.start_new_thread( _getHubStatus, (logger,))
        try:
            logging.info("Starting door watcher.")
            import RPIO
            RPIO.add_interrupt_callback(23, doorCallback, pull_up_down=RPIO.PUD_UP)
            RPIO.wait_for_interrupts(threaded=True, epoll_timeout=0.5)
            RPIO.setup(23, RPIO.IN, pull_up_down=RPIO.PUD_UP)
            if RPIO.input(23) is True:
                isDoorOpen = True
                logging.info("Door watcher running, door is open.")
            else:
                isDoorOpen = False
                logging.info("Door watcher running, door is closed.")
        except Exception, e:
            logging.warn("Unable to start door watcher: " + str(e))
    

def stopMonitor():
    global _tMonitorLoop
    logging.info("Stopping system status monitor.")
    _tMonitorLoop = False
    try:
        import RPIO
        RPIO.del_interrupt_callback(23)
        logging.info("Stopped door watcher.")
    except:
        pass
    logging.info("Stopped system status monitor.")


def _getHubStatus(logger):
    global hueBridgeIP, hueAppID, hueHubStatus, _tMonitorLoop, acStatus, away
    global itachIP, hueBridgeIP, isDoorOpen, insideTemperature

    logger.info("Starting Hue bridge monitor.\r")

    bridge = phue.Bridge(ip=hueBridgeIP, username=hueAppID)

    while _tMonitorLoop:
        data = bridge.get_api()
        hueHubStatus = data
        data["itachIP"] = itachIP
        data["hueBridgeIP"] = hueBridgeIP
        data["away"] = away
        data["airConditioners"] = acStatus
        data["isDoorOpen"] = isDoorOpen
        data["insideTemperature"] = insideTemperature()
        data["outsideTemperature"] = outsideTemperature()
        data["upTime"] = (datetime.now() - startTime).seconds
        data["updatedAt"] = str(datetime.now())
        data = json.dumps(data)
        with open("status.json", "w") as text_file:
            text_file.write(data)
        time.sleep(5)


def startAway():
    global away, awayArmed
    if away is True:
        logging.info("[AWAY] Already activated.")
    else:
        logging.info("[AWAY] System arming.")
        awayArmed = datetime.now() + timedelta(seconds=60)
        thread.start_new_thread( _armAway, (logging.getLogger(''),))


def stopAway():
    global away, awayArmed
    awayArmed = datetime.min
    if away is True:
        logging.info("[AWAY] Deactivated: Keyboard")
        away = False
        ledToggle(False)


def _armAway(logger):
    global away, awayArmed
    try:
        count = 0
        while datetime.now() < awayArmed:
            ledToggle(bool(count % 2))
            count = count + 1
            time.sleep(0.5)
        if awayArmed is not datetime.min:
            away = True
            ledToggle(True)
            logging.info("[AWAY] System activated.\r")
        else:
            ledToggle(False)

    except Exception, e:
        logging.info("Arm Away Error " + str(e) + "\r")
        pass


def ledToggle(pwr):
    try:
        import RPIO
        RPIO.setwarnings(False)
        RPIO.setup(24, RPIO.OUT)
        RPIO.output(24, pwr)
    except Exception, e:
        pass


def outsideTemperature(cached=True):
    try:
        last_updated = (datetime.now() - _outsideTemperature["time"]).total_seconds()
        if cached is True and last_updated < (60*30):
            return _outsideTemperature["temp"]
        conn = httplib.HTTPConnection("api.wunderground.com")
        conn.request("GET", "/api/KEY/conditions/q/40.69748809317884,-73.98093841395088.json")
        r1 = conn.getresponse()
        w = json.loads(r1.read())
        conn.close()
        _outsideTemperature["temp"] = int(w.get("current_observation").get("temp_f"))
        _outsideTemperature["time"] = datetime.now()
        logging.info("Outside Temperature: " + str(_outsideTemperature["temp"]) + "\r")
        return _outsideTemperature["temp"]
    except Exception, e:
        pass
        logging.error("Unable to get outdoor temperature. " + str(e) + "\r")
        return -1


def initTempSensor():
    global _tempSensorPath
    try:
        logging.info("Initalizing indoor temperature sensor.")
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        _tempSensorPath = device_folder + '/w1_slave'
        logging.info("Indoor temperature sensor ready.")
        return True
    except Exception, e:
        logging.error("Indoor temperature sensor error. " + str(e) + "\r")
        return False


def _readTemperatureSensor():
    global _tempSensorPath
    try:
        f = open(_tempSensorPath, 'r')
        lines = f.readlines()
        f.close()
        return lines
    except Exception, e:
        logging.error("Unable to read indoor temperature sensor: " + str(e) + "\r")
        return ""


def insideTemperature():
    global _tempSensorPath
    try:
        if _tempSensorPath is None:
            return -1
        else:
            lines = _readTemperatureSensor()
            while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = _readTemperatureSensor()
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                temp_f = temp_c * 9.0 / 5.0 + 32.0
                return temp_f
    except:
        return -1
