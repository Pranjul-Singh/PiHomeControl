import os
import Keys
import json
import time
import CloudLog
import glob
import httplib
import thread
from datetime import datetime

# o = {"enabled": True, "interval": 120, "location": "40.69748,-73.98093"}
# i = {"enabled": True, "interval": 30}

class Monitor:
  _component = "Temperature.Monitor"
  inside = {"temperature": None, "last_updated": 0}
  outside = {"temperature": None, "last_updated": 0}
  _outside_config = None
  _inside_config = None
  _run = False

  def __init__(self, outside_config, inside_config):
    CloudLog.log(self._component, "Initializing.")
    self._outside_config = outside_config
    self._inside_config = inside_config
    try:
      os.system('modprobe w1-gpio')
      os.system('modprobe w1-therm')
      base_dir = '/sys/bus/w1/devices/'
      device_folder = glob.glob(base_dir + '28*')[0]
      self._inside_config["sensor_path"] = device_folder + '/w1_slave'
      CloudLog.log(self._component, "Indoor temperature sensor ready.")
    except Exception, e:
      CloudLog.error(self._component, "Error initializing indoor temperature sensor", e)
      self._inside_config["enabled"] = False
    self.start()

  def __del__(self):
    self.stop()

  def start(self):
    if self._run is False:
      self._run = True
      try:
        thread.start_new_thread(self._runLoop, (None,))
      except Exception, e:
        CloudLog.error(self._component, "Unable to start temperature loop.", e)

  def stop(self):
    self._run = False

  def _runLoop(self, params):
    while self._run:
      current_time = int(datetime.now().strftime('%s')) * 1000
      # Read the outside temperature
      try:
        if ((current_time - self.outside["last_updated"]) > (self._outside_config["interval"] * 1000)) and self._outside_config["enabled"]:
          conn = httplib.HTTPConnection("api.wunderground.com")
          url = "/api/[KEY]/conditions/q/" + self._outside_config["location"] + ".json"
          conn.request("GET", url.replace("[KEY]", Keys.WEATHERBUG))
          r1 = conn.getresponse()
          w = json.loads(r1.read())
          conn.close()
          self.outside["temperature"] = int(w.get("current_observation").get("temp_f"))
          self.outside["last_updated"] = current_time
          #CloudLog.track("TEMPERATURE_OUTSIDE", str(self.outside["temperature"]))
      except Exception, e:
        CloudLog.error(self._component, "Error reading outside temperature", e)

      # Read the inside temperature
      try:
        if ((current_time - self.inside["last_updated"]) > (self._inside_config["interval"] * 1000)) and self._inside_config["enabled"]:
          lines = self._readTemperatureSensor()
          while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self._readTemperatureSensor()
          equals_pos = lines[1].find('t=')
          if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
          self.inside["temperature"] = temp_f
          self.inside["last_updated"] = current_time
          #CloudLog.track("TEMPERATURE_INSIDE", str(self.inside["temperature"]))
      except Exception, e:
        CloudLog.error(self._component, "Error reading inside temperature", e)

      time.sleep(10)

  def _readTemperatureSensor(self):
    try:
      f = open(self._inside_config["sensor_path"], 'r')
      lines = f.readlines()
      f.close()
      return lines
    except Exception, e:
      CloudLog.error(self._component, "Unable to read indoor temperature sensor", e)
      return ""
