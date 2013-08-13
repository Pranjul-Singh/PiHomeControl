import CloudLog
import thread
import time

class Monitor:
  _component = "DoorHandler"
  _controller = None
  _thread = None
  _doorOpen = None
  running = False
  state = None

  def __init__(self, controller):
    CloudLog.log(self._component, "Initializing.")
    self._controller = controller
    try:
      import RPIO
      self._start()
    except Exception, e:
      self.state = "NO_RPIO"
      CloudLog.error(self._component, "RPIO is unavailable.", e)
    

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
        previous_doorOpen = self._doorOpen
        import RPIO
        RPIO.setup(23, RPIO.IN, pull_up_down=RPIO.PUD_UP)
        self._doorOpen = RPIO.input(23)
        if previous_doorOpen != self._doorOpen:
          if self._doorOpen is True:
            self.state = "OPEN"
            if self._controller.state == "AWAY":
              self._controller.executeCommandByName("HOME")
          else:
            self.state = "CLOSED"
          CloudLog.track("FRONT_DOOR", self.state)
          # self._component.status(key="door", value=self.state)
        interval = 0.5
      except Exception, e:
        CloudLog.error(self._component, "Error in run loop", e)
        if interval < 10:
          interval += interval
      time.sleep(interval)
    CloudLog.log(self._component, "Stopped.")
