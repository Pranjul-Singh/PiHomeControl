import CloudLog
import httplib
import thread
import time
import Keys
import json

class Monitor:
  _component = "CloudHandler"
  _controller = None
  _settings = None
  _thread = None
  running = False

  def __init__(self, controller):
    self._settings = controller.config.settings["cloud_sync"]
    if self._settings["push"] or self._settings["pull"]:
      CloudLog.log(self._component, "Initializing.")
      self._controller = controller
      self._start()


  def stop(self):
    CloudLog.log(self._component, "Stopping.")
    self.running = False


  def _start(self):
    if self.running is False:
      self.running = True
      try:
        self._thread = thread.start_new_thread(self._runLoop, (None,))
      except Exception, e:
        CloudLog.error(self._component, "Unable to start run loop", e)


  def _runLoop(self, params):
    CloudLog.log(self._component, "Running.")
    while self.running:
      try:
        if self._settings["push"]:
          self._push()
        if self._settings["pull"]:
          self._pull()
        interval = self._settings["interval"]
      except Exception, e:
        CloudLog.error(self._component, "Error in run loop", e)
        if interval < self._interval * 10:
          interval += self._interval
      time.sleep(interval)
    CloudLog.log(self._component, "Stopped.")


  def _push(self):
    try:
      status = self._controller.status()
      status["app_engine_key"] = Keys.APPENGINE_USER
      content = json.dumps(status)
      self._query("POST", "/set/status", content)
    except Exception, e:
      CloudLog.error(self._component, "Error pushing system status.", e)


  def _pull(self):
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
