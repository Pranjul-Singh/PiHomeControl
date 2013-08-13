import CloudLog
import thread
import time

class Monitor:
  _component = "TestHandler"
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


  def _runLoop(self, params):
    CloudLog.log(self._component, "Running.")
    while self.running:
      try:
        self._controller.executeCommandByName("TEST")
        interval = 10
      except Exception, e:
        CloudLog.error(self._component, "Error in run loop", e)
        if interval < self._interval * 10:
          interval += self._interval
      time.sleep(interval)
    CloudLog.log(self._component, "Stopped.")
