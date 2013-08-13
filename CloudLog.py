import json
import Keys
import httplib
import logging

def init(log_file):
  logLevel = logging.INFO
  logFormat = '%(asctime)s | %(levelname)-7s | %(message)s'
  logging.basicConfig(format=logFormat, filename=log_file, level=logLevel)
  console = logging.StreamHandler()
  console.setLevel(logLevel)
  console.setFormatter(logging.Formatter(logFormat))

def debug(component, message, json_data=None, value=None, exception=None):
  DEBUG = False
  if DEBUG:
    component = "*" + component
    _sendToConsole(component, message, json_data, value, exception)
    _sendToLocalLog(component, message, json_data, value, exception)

def log(component, message):
  _sendToConsole(component, message)
  _sendToLocalLog(component, message)

def track(component, value):
  _sendToLocalLog(component, value)
  _sendToCloud(component, value)

def error(component, message, exception=None):
  logging.exception(component)
  if exception is not None:
    logging.info(str(exception))
  _sendToConsole(component, message, exception)
  _sendToLocalLog(component, message, exception)

def _stringify(component, message, json_data=None, value=None, exception=None):
  new_line = "\n\r"
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


def _sendToConsole(component, message, json_data=None, value=None, exception=None):
  log = _stringify(component, message, json_data, value, exception)
  print log

def _sendToLocalLog(component, message, json_data=None, value=None, exception=None):
  log = _stringify(component, message, json_data, value, exception)
  logging.info(log)


