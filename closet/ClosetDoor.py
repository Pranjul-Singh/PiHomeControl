import CloudLog
import time
import json
import socket

class Monitor:
  _component = "ClosetDoorHandler"
  _ip_address = None
  _port = None
  _doorOpen = False
  state = "NOT_READY"

  def __init__(self, ip_address, port):
    CloudLog.log(self._component, "Initializing.")
    self._ip_address = ip_address
    self._port = port
    try:
      import RPIO
      self.state = "READY"
    except Exception, e:
      self.state = "NO_RPIO"
      CloudLog.error(self._component, "RPIO is unavailable.", e)
    

  def run(self):
    CloudLog.log(self._component, "Running.")
    while self.state == "READY":
      try:
        previous_doorOpen = self._doorOpen
        import RPIO
        RPIO.setup(23, RPIO.IN, pull_up_down=RPIO.PUD_UP)
        self._doorOpen = RPIO.input(23)
        if previous_doorOpen != self._doorOpen:
          if self._doorOpen is True:
            self._announce("OPEN")
          else:
            self._announce("CLOSED")
        interval = 0.2
      except Exception, e:
        CloudLog.error(self._component, "Error in run loop", e)
        if interval < 10:
          interval += interval
      time.sleep(interval)
    CloudLog.log(self._component, "Stopped.")


  def _announce(self, state):
    try:
      CloudLog.track("CLOSET_DOOR", state)
      cmd = {"command": "CLOSET", "modifier": None}
      if state == "CLOSED":
        cmd["modifier"] = "Off"
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      sock.sendto(json.dumps(cmd), (self._ip_address, self._port))
      sock.close()
    except Exception, e:
      CloudLog.error(self._component, "Announce", e)
