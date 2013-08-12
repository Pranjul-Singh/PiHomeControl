import json
import socket
import CloudLog
import UDPListener

class Bridge:
  _component = "AirCon.Bridge"
  _search_ip = "239.255.250.250"
  _search_port = 9131
  _search_strings = ["AMXB<-UUID=GlobalCache_", "<-Model=iTachIP2IR>", "<-Status=Ready>"]
  _ready = False
  _ip_address = None
  _port = 4998
  _commands = None

  def __init__(self, commands, ip_address=None):
    CloudLog.log(self._component, "Initializing.")
    try:
      self._commands = commands
      if ip_address is None:
        self._ip_address = UDPListener.search(
          self._search_ip, self._search_port, self._search_strings)
      else:
        self._ip_address = ip_address
      self._ready = True
      CloudLog.log(self._component, "Ready. [" + str(self._ip_address) + "]")
    except Exception, e:
      CloudLog.error(self._component, "Error searching for iTach Device", e)

  def _sendCommand(self, device, command):
    result = {"completed": False, "request": {}}
    if device == "LR":
      device = "2"
    else:
      device = "3"
    cmd = "sendir,1:" + device + "," + command
    result["request"]["command"] = cmd
    if self._ready:
      try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((self._ip_address, self._port))
        s.send(cmd + "\r")
        response = s.recv(1024)
        s.close()
        result["completed"] = True
        result["response"] = str(response)
      except Exception, e:
        CloudLog.error(self._component, "Error when sending command", e)
    else:
      CloudLog.error(self._component, "Device not ready.")
    CloudLog.debug(self._component, json.dumps(result))
    return result

  def turn_on(self, device, temperature):
    CloudLog.track("AC_" + str(device), "On")
    cmd = self._commands["On"]
    self._sendCommand(device, cmd)
    self.set_temp(device, temperature)

  def turn_off(self, device):
    CloudLog.track("AC_" + str(device), "Off")
    cmd = self._commands["Off"]
    self._sendCommand(device, cmd)

  def set_temp(self, device, temperature):
    cmd = self._commands[temperature]
    self._sendCommand(device, cmd)

