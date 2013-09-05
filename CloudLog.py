import json
import Keys
import httplib
import logging
import logging.handlers
import SoundSystem

def init(log_file):
  # Setup the basic logging configuration
  logLevel = logging.INFO
  logFormat = '%(asctime)s | %(levelname)-7s | %(message)s'
  logging.basicConfig(level=logLevel, format=logFormat)
  # Setup the log to file
  logfile = logging.handlers.TimedRotatingFileHandler(log_file, when='W0', backupCount=10)
  logfile.setLevel(logLevel)
  logfile.setFormatter(logging.Formatter(logFormat))
  file_logger = logging.getLogger('file-logger')
  file_logger.addHandler(logfile)

def debug(component, message, json_data=None, value=None, exception=None):
  DEBUG = False
  if DEBUG:
    log = _stringify(component, message)
    file_logger.debug(log)

def log(component, message):
  file_logger = logging.getLogger('file-logger')
  log = _stringify(component, message)
  file_logger.info(log)

def track(component, value):
  file_logger = logging.getLogger('file-logger')
  file_logger.info(_stringify(component, value))
  _sendToCloud(component, value)

def error(component, message, exception=None):
  file_logger = logging.getLogger('file-logger')
  file_logger.exception(component)
  file_logger.debug(message)
  if exception is not None:
    file_logger.debug(str(exception))
  file_logger.debug("-- end --")
  try:
    SoundSystem.play('/sounds/error.mp3')
  except:
    pass

def _stringify(component, message, json_data=None, value=None, exception=None):
  new_line = "\r\n"
  json_data = None
  log = "[" + component + "] " + message
  try:
    seperator_line = False
    if json_data is not None:
      log += new_line + json.dumps(json_data)
      seperator_line = True
    if value is not None:
      log += new_line + str(value)
      seperator_line = True
    if exception is not None:
      log += new_line + str(exception)
      seperator_line = True
    if seperator_line == True:
      log += new_line + "---------------------------------------------------"
    return log
  except:
    return "LOG EXCEPTION " + log


def _sendToCloud(component, value):
  try:
    content = {}
    content["user_key"] = Keys.APPENGINE_USER
    content["component"] = component
    content["value"] = value
    content = json.dumps(content)
    headers = {}
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "*/*"
    conn = httplib.HTTPSConnection("petele-home-automation.appspot.com")
    conn.request("POST", "/track/", content, headers)
    response = conn.getresponse()
    if response.status != 200:
      error("SendToCloud", "Server side error syncing track data to cloud.")
    conn.close()
  except Exception, e:
    error("SendToCloud", "Client side error syncing track data to cloud.", e)
