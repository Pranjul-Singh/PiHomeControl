import json
import time
import random
import socket
import thread
import CloudLog

class Monitor:
  _component = "UDPHandler"
  _controller = None
  _settings = None
  _threadAnnounce = None
  _threadListen = None
  running = False


  def __init__(self, controller):
    self._settings = controller.config.settings["udp_listener"]
    self._controller = controller
    if self._settings["announce"]:
      self.running = True
      self._startAnnounce()
    if self._settings["listen"]:
      self.running = True
      self._startListen()


  def stop(self):
    CloudLog.log(self._component, "Stopping.")
    self.running = False


  def _startAnnounce(self):
    if self._threadAnnounce is None:
      try:
        CloudLog.log(self._component + ":StartAnnounce", "Starting UDP Announcer")
        self._threadAnnounce = thread.start_new_thread(self._runAnnounceLoop, (None,))
      except Exception, e:
        CloudLog.error(self._component, "Unable to start announce loop", e)


  def _startListen(self):
    if self._threadListen is None:
      try:
        CloudLog.log(self._component + ":StartListen", "Starting UDP Listener")
        self._thread = thread.start_new_thread(self._runListenLoop, (None,))
      except Exception, e:
        CloudLog.error(self._component, "Unable to start listen loop", e)


  def _runAnnounceLoop(self, params):
    udp_socket = None
    try:
      port = 9337
      ip = "239.2.2.4"
      udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 4)
      udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    except Exception, e:
      udp_socket = None
      CloudLog.error(self._component, "Error opening announce multicast socket", e)

    while self.running and udp_socket is not None:
      try:
        udp_socket.sendto("PiHomeControl", (ip, port))
      except Exception, e:
        pass
      time.sleep(45 + random.randint(15,30))


  def _runListenLoop(self, params):
    udp_socket = None
    try:
      ip = "192.168.1.201"
      port = 9557
      udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      udp_socket.bind((ip, port))
    except Exception, e:
      self._running = False
      udp_socket = None
      CloudLog.error(self._component, "Error opening socket", e)

    while self.running and udp_socket is not None:
      try:
        packet = udp_socket.recvfrom(1024)
        result = json.loads(packet[0])
        cmd = result["command"]
        if cmd == "RELOAD_CONFIG":
          self._controller.config.read()
          CloudLog.log(self._component + ":Config", "Reload")
        else:
          modifier = result.get("modifier")
          CloudLog.log(self._component + ":Execute", cmd + ":" + str(modifier))
          self._controller.executeCommandByName(cmd, modifier)
        interval = 0.1
      except Exception, e:
        CloudLog.error(self._component, "Error in run loop", e)
        if interval < 10:
          interval += 1
      time.sleep(interval)
    udp_socket.close()
    CloudLog.log(self._component, "Stopped.")
