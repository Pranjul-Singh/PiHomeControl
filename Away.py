import CloudLog
import thread
import random
import time


class Monitor:
  _component = "AwayHandler"
  _controller = None
  _thread = None
  running = False

  def __init__(self, controller):
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
        self.running = False


  def _runLoop(self, params):
    CloudLog.log(self._component, "Running.")
    interval = 300
    while self.running:
      time.sleep(interval)
      try:
        if self._controller.state == "AWAY":
          state = self._controller.status()
          hue_status = state["hue"]
          any_on = False
          for light in hue_status["lights"]:
            if hue_status["lights"][light]["state"]["on"] is True:
              any_on = True
          if any_on is True:
            self._controller.executeCommandByName("LIGHTSOFF")
        interval = 300
      except Exception, e:
        CloudLog.error(self._component, "Error in _runLoop", e)
        if interval < 3000:
          interval += random.randint(120,300)
    CloudLog.log(self._component, "Stopped.")
