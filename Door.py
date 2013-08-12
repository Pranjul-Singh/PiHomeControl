import CloudLog
import thread
import time

class Monitor:
  state = None
  _component = "Door.Monitor"
  _run = False
  _callback = None

  def __init__(self, callback=None):
    CloudLog.log(self._component, "Initializing.")
    try:
      import RPIO
      self.update()
      self._callback = callback
      CloudLog.log(self._component, "Door is " + self.state)
      self.start()
      CloudLog.log(self._component, "Ready.")
    except Exception, e:
      self.state = "NO_RPIO"
      CloudLog.error(self._component, "RPIO is unavailable.", e)

  def __del__(self):
    self.stop()

  def start(self):
    if self._run is False:
      self._run = True
      try:
        thread.start_new_thread(self._runLoop, (None,))
      except Exception, e:
        CloudLog.error(self._component, "Unable to start Door Watch loop.", e)

  def stop(self):
    self._run = False

  def _runLoop(self, params):
    while self._run:
      try:
        previous = self.state
        self.update()
        if previous != self.state:
          CloudLog.track("FRONT_DOOR", self.state)
          if self._callback is not None:
            self._callback(self.state)
      except Exception, e:
        CloudLog.error(self._component, "Error in runLoop", e)
      time.sleep(0.5)

  def update(self):
    try:
      import RPIO
      RPIO.setup(23, RPIO.IN, pull_up_down=RPIO.PUD_UP)
      if RPIO.input(23) is True:
        self.state = "OPEN"
      else:
        self.state = "CLOSED"
    except Exception, e:
      CloudLog.error(self._component, "Error reading current door state.", e)
      self.state = "ERROR"
    return self.state