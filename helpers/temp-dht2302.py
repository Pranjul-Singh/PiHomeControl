import logging
import subprocess
import re
#import sys
import time
#import datetime
#import gspread


def getTemp():
    _temp = None
    _humidity = None
    _errors = 0
    while _temp is None or _humidity is None:
        print str(_temp)
        print str(_humidity)
        try:
            output = subprocess.check_output(["./Adafruit_DHT", "2302", "4"]);
            matches = re.search("Temp =\s+([0-9.]+)", output)
            _temp = float(matches.group(1))
            matches = re.search("Hum =\s+([0-9.]+)", output)
            _humidity = float(matches.group(1))
        except Exception, e:
            time.sleep(3)
            _errors = _errors + 1
            if (_errors == 3):
                _temp = -1
                _humidity = -1
            print "Error reading indoor weather"

    return {"temperature": _temp, "humidity": _humidity}


while True:
    print getTemp()
    time.sleep(10)

    

    # if (not matches):
    #     time.sleep(3)
    #     continue
    # temp = float(matches.group(1))

    # matches = re.search("Hum =\s+([0-9.]+)", output)
    # if (not matches):
    #     time.sleep(3)
    #     continue
    # humidity = float(matches.group(1))

    # print "Temperature: %.1f C" % temp
    # print "Humidity:    %.1f %%" % humidity
    # 