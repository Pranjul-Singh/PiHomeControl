import CloudLog
import json

class Config:
  _component = "Config"
  _config_file = "config.json"
  settings = {}
  ac_commands = {}
  light_recipes = {}
  harmony_activities = {}
  commands = {}
  commands_by_name = {}
  commands_by_key = {}

  def __init__(self):
    CloudLog.log(self._component, "Initializing")
    self.read()

  def read(self):
    try:
      with open(self._config_file, "r") as text_file:
        results = text_file.read()
      cfg = json.loads(results)
      self.settings = cfg["config"]
      self.ac_commands = cfg["ac_commands"]
      self.light_recipes = cfg["light_recipes"]
      self.harmony_activities = cfg["harmony_activities"]
      self.commands = cfg["commands"]
      for command in self.commands:
        key = command.get("key")
        name = command.get("name")
        if key is not None:
          self.commands_by_key[key] = command
        if name is not None:
          self.commands_by_name[name] = command
      CloudLog.log(self._component, "Config file loaded.")
    except Exception, e:
      CloudLog.error(self._component, "Error reading config file.", e)

  def save(self):
    try:
      CloudLog.log(self._component, "Saving config file.")
      new_config = {}
      new_config["config"] = self.settings
      new_config["ac_commands"] = self.ac_commands
      new_config["light_recipes"] = self.light_recipes
      new_config["harmony_activities"] = self.harmony_activities
      new_config["commands"] = self.commands
      result = json.dumps(new_config)
      with open(self._config_file, "w") as text_file:
        text_file.write(result)
    except Exception, e:
      CloudLog.error(self._component, "Error saving config file.", e)

  def get_activity_name(self, activity_id):
    try:
      if activity_id is None:
        return "NONE"
      for act_name, act_id in self.harmony_activities.iteritems():
        if str(act_id) == str(activity_id):
          return str(act_name)
      return "UNKNOWN"
    except Exception, e:
      CloudLog.error(self._component, "Error getting activity name.", e)
