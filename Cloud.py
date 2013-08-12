import json
import Keys
import time
import thread
import httplib
import CloudLog

class Manager:
  _component = "Cloud.Manager"
  _controller = None
  _config = None
  _interval = None
  _run = False

  def __init__(self, controller, config):
    CloudLog.log(self._component, "Initializing.")
    try:
      self._controller = controller
      self._config = config
      self._run = True
      self._interval = self._config.settings["cloud_sync"]["interval"]
      if self._config.settings["cloud_sync"]["push"] is True:
        thread.start_new_thread(self._pushLoop, (None,))
      if self._config.settings["cloud_sync"]["pull"] is True:
        thread.start_new_thread(self._pullLoop, (None,))
      CloudLog.log(self._component, "Ready.")
    except Exception, e:
      CloudLog.error(self._component, "Error initializing Cloud Manager.", e)
    pass

  def __del__(self):
    CloudLog.log(self._component, "Destructor")
    self._run = False


  def _pullLoop(self, params):
    while self._run is True:
      try:
        self.pull()
      except Exception, e:
        CloudLog.error(self._component, "Error when pulling", e)
      time.sleep(self._interval)

  def pull(self):
    try:
      commands = []
      result = self._query("GET", "/get/cmds?clear=true", "")
      commands = json.loads(result)
    except Exception, e:
      return
    for command in commands:
      try:
        cmd = command["command"]
        modifier = command.get("modifier")
        CloudLog.log(self._component + ":Pull", cmd + ":" + str(modifier))
        self._controller.executeCommandByName(cmd, modifier)
      except Exception, e:
        CloudLog.error(self._component, "Error executing command", e)


  def _pushLoop(self, params):
    while self._run is True:
      try:
        self.push()
      except Exception, e:
        CloudLog.error(self._component, "Error when pushing data", e)
      time.sleep(self._interval)

  def push(self):
    try:
      status = self._controller.status()
      status["app_engine_key"] = Keys.APPENGINE_USER
      content = json.dumps(status)
      self._query("POST", "/set/status", content)
    except Exception, e:
      CloudLog.error(self._component, "Error pushing system status.", e)

  def _query(self, method, url, content):
    try:
      headers = {}
      headers["Content-Type"] = "application/json"
      headers["Accept"] = "*/*"
      conn = httplib.HTTPSConnection("petele-home-automation.appspot.com")
      conn.request(method, url, content, headers)
      response = conn.getresponse()
      if response.status != 200:
        CloudLog.error(self._component, "Error updating system status.")
      conn.close()
      return response.read()
    except Exception, e:
      CloudLog.error(self._component, "Exception while updating system status.", e)
