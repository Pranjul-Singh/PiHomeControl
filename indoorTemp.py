#!/usr/bin/env python

import os
import glob
import time
import logging

_tempSensorPath = None


def init():
    global _tempSensorPath

    try:
        logging.info("Initalizing indoor temperature sensor.\r")
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        _tempSensorPath = device_folder + '/w1_slave'
        logging.info("Indoor temperature sensor ready.\r")
        return True
    except Exception, e:
        logging.error("Indoor temperature sensor error. " + str(e) + "\r")
        return False


def get():
    global _tempSensorPath

    try:
        if _tempSensorPath is None:
            return None
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
        return None


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
