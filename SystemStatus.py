#!/usr/bin/env python

import phue
import time
import json
import thread
import macros
import logging
import httplib
import indoorTemp
import HarmonyHub
from subprocess import Popen, PIPE
from datetime import datetime, timedelta

itachIP = None
hueBridgeIP = None
harmonyIP = None
hueAppID = "9075e416a7d67c2f6c7d9386dff2e591"

_armAwayAt = datetime.min

_monitorLoop = False
_startTime = None
_isDoorOpen = False
_isAway = False
_acState = None
_gVoiceMessages = None
_gVoiceLightOn = None
_insideTemp = None
_outsideTemp = None
_hueState = None
_harmonyState = None

def start():
  global _monitorLoop, _startTime

  logging.info("Starting system status monitor.")
  _monitorLoop = True
  _startTime = (float(datetime.now().strftime('%s.%f')) * 1000)
  _initAC()
  _startDoorWatcher()
  _startHueMonitor()
  _startHarmonyMonitor()
  _startInsideTempMonitor()
  _startOutsideTempMonitor()
  _startGVoiceMonitor()
  setLED(0, True)


def stop():
  global _monitorLoop
  logging.info("Stopping system status monitor.")
  _monitorLoop = False
  setLED(0, False)


def get():
  global _startTime, _monitorLoop, _isAway, _isDoorOpen, _acState, _hueState
  global _insideTemp, _outsideTemp, _gVoiceMessages, _harmonyState
  global hueBridgeIP, itachIP, harmonyIP
  result = {}
  result["systemTime"] = (float(datetime.now().strftime('%s.%f')) * 1000)
  result["startTime"] = _startTime
  result["monitorRunning"] = _monitorLoop
  result["away"] = _isAway
  result["doorOpen"] = _isDoorOpen
  result["airConditioners"] = _acState
  result["hueState"] = _hueState
  result["harmonyState"] = _harmonyState
  result["insideTemperature"] = _insideTemp
  result["outsideTemperature"] = _outsideTemp
  result["hueBridgeIP"] = hueBridgeIP
  result["itachIP"] = itachIP
  result["harmonyIP"] = harmonyIP
  result["gVoiceMessages"] = _gVoiceMessages
  return result


def saveToDisk(filename):
  result = get()
  with open(filename, "w") as text_file:
    text_file.write(result)


def setAway(away):
  global _isAway, _armAwayAt, _gVoiceLightOn

  if away is True and _isAway is False:
    logging.info("[AWAY] System arming.")
    _gVoiceLightOn = False
    _armAwayAt = datetime.now() + timedelta(seconds=60)
    thread.start_new_thread( _armAway, (logging.getLogger(''),))
  elif away is False and _isAway is True:
    _isAway = False
    _armAwayAt = datetime.min
    setLED(1, False)
    logging.info("[AWAY] Deactivated: Keyboard.")
  else:
    # logging.info("[AWAY] Mode already set.")
    pass


def setLED(led_id, on):
  # logging.info("Set LED: " + str(led_id) + " on: " + str(on) + "\r")
  try:
    import RPIO
    pin = 24
    RPIO.setwarnings(False)
    RPIO.setup(pin, RPIO.OUT)
    RPIO.output(pin, on)
  except Exception, e:
    pass

def _armAway(logger):
  global _isAway, _armAwayAt
  try:
    count = 0
    while datetime.now() < _armAwayAt:
      setLED(1, bool(count % 2))
      count += 1
      time.sleep(0.5)
    if _armAwayAt is not datetime.min:
      _isAway = True
      setLED(1, True)
      logging.info("[AWAY] System activated.\r")
    else:
      setLED(1, False)
  except Exception, e:
    logging.info("Arm Away Error: " + str(e) + "\r")
    setLED(1, False)


def _initAC():
  global _acState
  logging.info("Initalizing air conditioner status.")
  _acState = {
    "AC-BED": {
      "mode": "OFF",
      "temperature": -1,
      "fan": "OFF"
    },
    "AC-LR": {
      "mode": "OFF",
      "temperature": -1,
      "fan": "OFF"
    }
  }


def _startDoorWatcher():
  global _isDoorOpen
  try:
    logging.info("Starting door watcher.")
    import RPIO
    thread.start_new_thread( _doorWatcher, (logging.getLogger(''),))
    RPIO.setup(23, RPIO.IN, pull_up_down=RPIO.PUD_UP)
    if RPIO.input(23) is True:
      _isDoorOpen = True
      logging.info("Door watcher running, door is open.")
    else:
      _isDoorOpen = False
      logging.info("Door watcher running, door is closed.")
  except Exception, e:
      logging.warn("Unable to start door watcher: " + str(e))


def _doorWatcher(logger):
  global _isDoorOpen, _monitorLoop, _isAway

  errorTimer = 60
  while _monitorLoop:
    try:
      import RPIO
      RPIO.setup(23, RPIO.IN, pull_up_down=RPIO.PUD_UP)
      newState = RPIO.input(23)
      if newState != _isDoorOpen:
        _isDoorOpen = newState
        if _isDoorOpen is True:
          logger.info("Door opened.\r")
          if _isAway is True:
            _isAway = False
            macros.execute("H", None)
            logger.info("[AWAY] Deactivated: Door\r")
        else:
          logger.info("Door closed.\r")
      time.sleep(1)
      errorTimer = 60
    except Exception, e:
      logging.error("Error reading door state: " + str(e) + "\r")
      time.sleep(errorTimer)
      if errorTimer < 600:
        errorTimer += 60


def _startHueMonitor():
  thread.start_new_thread( _hueMonitor, (logging.getLogger(''),))


def _hueMonitor(logger):
  global _monitorLoop, _hueState, hueBridgeIP, hueAppID

  errorTimer = 60
  logger.info("Starting Hue bridge monitor.\r")
  bridge = phue.Bridge(ip=hueBridgeIP, username=hueAppID)
  while _monitorLoop:
    try:
      _hueState = bridge.get_api()
      time.sleep(5)
      errorTimer = 60
    except Exception, e:
      _hueState = None
      logger.error("Error reading Hue Hub state: " + str(e) + "\r")
      time.sleep(errorTimer)
      if errorTimer <= 600:
        errorTimer += 60


def _startHarmonyMonitor():
  thread.start_new_thread( _harmonyMonitor, (logging.getLogger(''),))


def _harmonyMonitor(logger):
  global _monitorLoop, _harmonyState

  errorTimer = 60
  logger.info("Starting Harmony monitor\r")
  while _monitorLoop:
    try:
      _harmonyState = HarmonyHub.getCurrentActivity()
      time.sleep(60)
      errorTimer = 60
    except Exception, e:
      _harmonyState = None
      logger.error("Error reading Harmony state: " + str(e) + "\r")
      time.sleep(errorTimer)
      if errorTimer <= 600:
        errorTimer += 60


def _startInsideTempMonitor():
  ready = indoorTemp.init()
  if ready is True:
    thread.start_new_thread( _insideTempMonitor, (logging.getLogger(''),))
  else:
    logging.error("Unable to start inside temperature monitor, init failed.\r")


def _insideTempMonitor(logger):
  global _monitorLoop, _insideTemp

  errorTimer = 60
  logger.info("Starting inside temperature monitor.\r")
  while _monitorLoop:
    try:
      _insideTemp = indoorTemp.get()
      time.sleep(30)
      errorTimer = 60
    except Exception, e:
      _insideTemp = None
      logger.error("Unable to get indoor temperature. " + str(e) + "\r")
      time.sleep(errorTimer)
      if errorTimer <= 600:
        errorTimer += 60


def _startOutsideTempMonitor():
  thread.start_new_thread( _outsideTempMonitor, (logging.getLogger(''),))


def _outsideTempMonitor(logger):
  global _monitorLoop, _outsideTemp

  errorTimer = 60
  logger.info("Starting weather monitor.\r")
  while _monitorLoop:
    try:
      conn = httplib.HTTPConnection("api.wunderground.com")
      url = "/api/[KEY]/conditions/q/40.69748,-73.98093.json"
      conn.request("GET", url.replace("[KEY]", "a686072a8a6d09d3"))
      r1 = conn.getresponse()
      w = json.loads(r1.read())
      conn.close()
      _outsideTemp = int(w.get("current_observation").get("temp_f"))
      time.sleep(60*30)
      errorTimer = 60
    except Exception, e:
      _outsideTemp = None
      logger.error("Unable to get outdoor temperature. " + str(e) + "\r")
      time.sleep(errorTimer)
      if errorTimer <= 600:
        errorTimer += 60


def _startGVoiceMonitor():
  global _gVoiceLightOn

  _gVoiceLightOn = False
  thread.start_new_thread( _gvoiceMonitor, (logging.getLogger(''),))


def _gvoiceMonitor(logger):
  global _monitorLoop, _gVoiceMessages, _gVoiceLightOn, _isAway

  errorTimer = 60
  logger.info("Starting Google Voice message monitor.\r")
  while _monitorLoop:
    if _isAway is True:
      time.sleep(30)
    else:
      try:
        output = Popen(['lynx', '-source', 'https://www.google.com/voice/request/unread'], stdout=PIPE)
        resp = output.stdout.read()
        _gVoiceMessages = json.loads(resp)
        if _gVoiceMessages.get("unreadCounts").get("all") > 0:
          if _gVoiceLightOn is False:
            macros.execute("GV", None)
            _gVoiceLightOn = True
        else:
          if _gVoiceLightOn is True:
            macros.execute("GV", "Off")
            _gVoiceLightOn = False
        time.sleep(10)
        errorTimer = 60
      except Exception, e:
        logger.error("Unable to get Google Voice message data: " + str(e) + "\r")
        _gVoiceMessages = json.loads('{"error": "' + str(e) + '"}')
        macros.execute("GV", "NightRed")
        time.sleep(errorTimer)
        if errorTimer <= 600:
          errorTimer += 60
