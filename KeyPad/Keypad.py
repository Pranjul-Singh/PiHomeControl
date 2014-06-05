import CloudLog
from getch import GetCh
from datetime import datetime, timedelta


def listen(ip_address, port):
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
      if charInput == "\r":
        charInput = "H"
        modifier = None
      elif charInput == "0":
        modifier = None  
      CloudLog.log(component + ":KeyPress", charInput + ":" + str(modifier))
      sendCommand(ip_address, port, charInput, modifier)
      # controller.executeCommandByKeyCode(charInput, modifier)
      modifier = None
      modTimer = datetime.min


def sendCommand(ip_address, port, charInput, modifier):
  pass