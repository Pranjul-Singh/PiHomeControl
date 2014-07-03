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
  _status = { "LR": "Off", "BR": "Off", "KI": "Off" }

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
      device = "1"
    elif device == "BR":
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

  def _send(self, device, command):
    result = {"completed": False, "request": {}}
    try:
      if device == "LR":
        port = "1"
        protocol = "FR"
      elif device == "BR":
        port = "2"
        protocol = "LG"
      else:
        port = "3"
        protocol = "FR"
      cmd = "sendir,1:" + port + "," + self._commands[protocol][command]
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
    except:
      pass
    return result

  def turn_on(self, device, temperature):
    CloudLog.track("AC_" + str(device), "On")
    self._send(device, "On")
    self._send(device, temperature)
    self._status[device] = temperature

  def turn_off(self, device):
    CloudLog.track("AC_" + str(device), "Off")
    self._send(device, "Off")
    self._status[device] = "Off"

  def fan(self, device, speed):
    CloudLog.track("AC_" + str(device), speed)
    self._send(device, speed)
    self._status[device] = speed

  def fast_cool(self, device):
    CloudLog.track("AC_" + str(device), "FastCool")
    if self._status[device] == "Off":
      self._send(device, "On")
    self._send(device, "FC")
    self._status[device] = "65"

  def change_temp(self, device, dir):
    try:
      new_temp = self._status[device]
      new_temp = int(new_temp)
      if dir.upper() == "UP":
        new_temp = new_temp + 1
      else:
        new_temp = new_temp - 1
      print ("NewTemp", new_temp)
      self.set_temp(device, str(new_temp))
    except:
      CloudLog.error(self._component, "Cannot change temp.")

  def set_temp(self, device, temperature):
    try:
      temperature = int(temperature)
      if temperature >= 60 and temperature <= 75:
        self._send(device, str(temperature))
        self._status[device] = temperature
      else:
        CloudLog.error(self._component, "Cannot change temp.")
    except:
      CloudLog.error(self._component, "Temp out of range")

  def status(self):
    return self._status


