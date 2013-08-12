import CloudLog
import thread
import time
import json
from subprocess import Popen, PIPE


class Monitor:
  _component = "GVoice.Monitor"
  messages = 0
  _config = None
  _run = False
  _callback = None

  def __init__(self, config, callback):
    CloudLog.log(self._component, "Initializing.")
    self._callback = callback
    self._config = config
    self.start()
    CloudLog.log(self._component, "Ready.")
  def __del__(self):
    self.stop()

  def start(self):
    if self._run is False and self._config["enabled"]:
      self._run = True
      try:
        thread.start_new_thread(self._runLoop, (None,))
      except Exception, e:
        CloudLog.error(self._component, "Unable to start GoogleVoice loop.", e)

  def stop(self):
    self._run = False

  def _runLoop(self, params):
    while self._run:
      old_count = self.messages
      try:
        output = Popen(['lynx', '-source', 'https://www.google.com/voice/request/unread'], stdout=PIPE)
        response = output.stdout.read()
        response = json.loads(response)
        self.messages = int(response["unreadCounts"]["all"])
        if self._callback is not None:
          if self.messages > old_count:
            self._callback(self.messages)
          elif self.messages == 0 and old_count > 0:
            self._callback(self.messages)
      except Exception, e:
        CloudLog.error(self._component, "Unable to read message count.", e)
        if self._callback is not None:
          self._callback(-1)
      time.sleep(self._config["interval"])
