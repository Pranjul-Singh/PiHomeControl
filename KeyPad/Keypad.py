import CloudLog
import logging
import json
import socket
from getch import GetCh
from datetime import datetime, timedelta

class Monitor:
  _component = "KeypadHandler"
  _ip_address = None
  _port = None
  _commands = None

  def __init__(self, ip_address, port):
    CloudLog.log(self._component, "Initializing.")
    self._ip_address = ip_address
    self._port = port
    with open("config.json", "r") as text_file:
      results = text_file.read()
    self._commands = json.loads(results)


  def run(self):
    component = "KeyPadController"
    runLoop = True
    modifier = None
    modTimer = datetime.min
    keyModifier = {
      "\t": "Off",
      "/": "VirginBlue",
      "*": "NightRed",
      "\x7f": "DimWhite",
      "+": "UP",
      "-": "DOWN"
    }

    while runLoop:
      CloudLog.debug(component, "Waiting for key")
      charInput = GetCh()
      CloudLog.debug(component, "Got Key")
      if modTimer + timedelta(seconds=4) < datetime.now():
        modifier = None
        modTimer = datetime.min
      if charInput == "q" or charInput == "Q":
        CloudLog.log(component, "User Interupt (Q)")
        runLoop = False
      elif keyModifier.get(charInput) is not None:
        modifier = keyModifier.get(charInput)
        modTimer = datetime.now()
      else:
        CloudLog.log(component + ":KeyPress", charInput + ":" + str(modifier))
        try:
          command = self._commands[charInput]
          self._announce({"command": command, "modifier": modifier})
        except:
          pass
        modifier = None
        modTimer = datetime.min


  def _announce(self, command):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps(command), (self._ip_address, self._port))
    sock.close()

