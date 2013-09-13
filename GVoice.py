import CloudLog
import thread
import time
import json
from subprocess import Popen, PIPE

class Monitor:
  _component = "GVoice"
  _controller = None
  _settings = None
  _thread = None
  running = False
  unread = None

  def __init__(self, controller):
    self._settings = controller.config.settings["gvoice"]
    if self._settings["enabled"]:
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
    interval = self._settings["interval"]
    if self.unread is None:
      self.unread = 0
    while self.running:
      try:
        if self._controller.state == "HOME":
          output = Popen(['lynx', '-source', 'https://www.google.com/voice/request/unread'], stdout=PIPE)
          response = output.stdout.read()
          response = json.loads(response)
          previous_count = self.unread
          self.unread = int(response["unreadCounts"]["all"])
          if self.unread > previous_count:
            cmd = self._settings["cmd_new"]
            self._controller.executeCommandByName(cmd)
          elif self.unread == 0 and previous_count > 0:
            cmd = self._settings["cmd_zero"]
            self._controller.executeCommandByName(cmd)
          interval = self._settings["interval"]
        else:
          interval = self._settings["interval"] * 2
      except Exception, e:
        CloudLog.error(self._component, "Error in run loop", e)
        cmd = self._settings["cmd_error"]
        self._controller.executeCommandByName(cmd)
        if interval < self._settings["interval"] * 10:
          interval += interval
      time.sleep(interval)
    CloudLog.log(self._component, "Stopped.")
