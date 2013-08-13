import Hue
import AirCon
import Harmony
import CloudLog
import Temperature
import SoundSystem
from threading import Timer
from datetime import datetime

class Controller:
  state = "AWAY"
  config = None
  _handlers = {}
  _aircon = None
  _hue = None
  _harmony = None
  _temperature = None
  _status = {
    "ac": {"LR": "Off", "BR": "Off"},
    "time": {"start": ""}
  }
  _away_timer = None


  def __init__(self, config):
    self._status["time"]["start"] = int(datetime.now().strftime('%s')) * 1000
    self.config = config

    self._aircon = AirCon.Bridge(config.ac_commands)
    self._hue = Hue.Bridge()
    self._harmony = Harmony.Bridge()
    self._temperature = Temperature.Monitor(
     config.settings["outside_temperature"],
     config.settings["inside_temperature"])
    SoundSystem.play(config.settings["ready_sound"])


  def status(self):
    status = self._status
    status["system_state"] = self.state
    try:
      act_id = self._harmony.currentActivity()["response"]
      status["harmony_activity"] = self.config.get_activity_name(act_id)
    except:
      status["harmony_activity"] = "ERROR"
    status["door"] = self._handlers["Door.Monitor"].state
    status["time"]["updated"] = int(datetime.now().strftime('%s')) * 1000
    try:
      status["hue"] = self._hue.status()["response"]
    except:
      status["hue"] = "ERROR"
    try:
      status["temperature"] = {}
      status["temperature"]["inside"] = self._temperature.inside["temperature"]
      status["temperature"]["outside"] = self._temperature.outside["temperature"]
    except:
      status["temperature"] = {}
      status["temperature"]["inside"] = None
      status["temperature"]["outside"] = None
    return status

  
  def addHandler(self, handler):
    CloudLog.log("System:AddHandler", str(handler))
    try:
      handler_name = str(handler)
      handler_instance = handler(self)
      self._handlers[handler_name] = handler_instance
    except Exception, e:
      CloudLog.error("System:AddHandler", "Error adding handler.", e)


  def _setState(self, new_state):
    if new_state == "AWAY":
      if self._away_timer is not None:
        self._away_timer.cancel()
      new_state = "ARMED"
      self._away_timer = Timer(90.0, self._setAway)
      self._away_timer.start()
    self.state = new_state
    CloudLog.track("STATE", new_state)


  def _setAway(self):
    if self.state == "ARMED":
      self.state = "AWAY"
      CloudLog.track("STATE", "AWAY")
    self._away_timer = None


  def shutdown(self):
    component = "System:ShutDown"
    self._setState("SHUTDOWN")
    for key, handler in self._handlers.iteritems():
      handler.stop()
    self._temperature.stop()
    self._status["time"]["shutdown"] = int(datetime.now().strftime('%s')) * 1000
    CloudLog.log(component, "System Shutdown")


  def _executeCommand(self, command, modifier=None):
    component = "System:ExecuteCommand"
    CloudLog.log(component, command["name"])
    if command.get("lights") is not None:
      for light in command["lights"]:
        try:
          if modifier is not None:
            cmd = self.config.light_recipes[modifier]
          else:
            cmd = self.config.light_recipes[light["command"]]
          self._hue.sendCommand(light["lights"], cmd)
        except Exception, e:
          CloudLog.error("System:executeCommand", "Lights", e)
    if command.get("ac") is not None:
      for ac in command["ac"]:
        try:
          if modifier == "Off" or ac["state"] == "Off":
            self._aircon.turn_off(ac["device"])
            self._status["ac"][ac["device"]] = "Off"
          elif modifier == "UP":
            try:
              temperature = str(int(self._status["ac"][ac["device"]]) + 1)
              self._aircon.set_temp(ac["device"], temperature)
              self._status["ac"][ac["device"]] = temperature
            except:
              pass
          elif modifier == "DOWN":
            try:
              temperature = str(int(self._status["ac"][ac["device"]]) - 1)
              self._aircon.set_temp(ac["device"], temperature)
              self._status["ac"][ac["device"]] = temperature
            except:
              pass
          elif ac["state"] == "On":
            temperature = self.config.settings["ac_default_temp"]
            self._aircon.turn_on(ac["device"], temperature)
            self._status["ac"][ac["device"]] = temperature
          elif ac["state"] == "Auto":
            turn_on = False
            threshold = self.config.settings["temperature_threshold"]
            if self._temperature.inside["temperature"] is not None:
              if self._temperature.inside["temperature"] > threshold["inside"]:
                turn_on = True
            if self._temperature.outside["temperature"] is not None:
              if self._temperature.outside["temperature"] > threshold["outside"]:
                turn_on = True
            if turn_on:
              temperature = self.config.settings["ac_default_temp"]
              self._aircon.turn_on(ac["device"], temperature)
              self._status["ac"][ac["device"]] = temperature
        except Exception, e:
          CloudLog.error("System:executeCommand", "AC", e)
    if command.get("harmony") is not None:
      try:
        activity_id = self.config.harmony_activities.get(command.get("harmony"))
        self._harmony.startActivity(activity_id)
      except Exception, e:
        CloudLog.error("System:executeCommand", "Harmony", e)
    if command.get("sound") is not None:
      try:
        SoundSystem.play(command["sound"])
      except Exception, e:
        CloudLog.error("System:executeCommand", "Sound", e)
    if command.get("system_state") is not None:
      self._setState(command["system_state"])


  def executeCommandByName(self, command_name, modifier=None):
    command = self.config.commands_by_name.get(command_name)
    if command is not None:
      self._executeCommand(command, modifier)


  def executeCommandByKeyCode(self, key_code, modifier=None):
    command = self.config.commands_by_key.get(key_code)
    if command is not None:
      self._executeCommand(command, modifier)
