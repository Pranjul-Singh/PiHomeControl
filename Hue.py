import json
import phue
import CloudLog
import UDPListener

class Bridge:
  _component = "Hue.Bridge"
  _search_ip = "239.255.255.250"
  _search_port = 1900
  _search_strings = ["NOTIFY * HTTP/1.1", ":80/description.xml"]
  _ready = False
  _phue = None
  _hueAppID = "9075e416a7d67c2f6c7d9386dff2e591"
  

  def __init__(self, ip_address=None):
    CloudLog.log(self._component, "Initializing.")
    try:
      if ip_address is None:
        ip_address = UDPListener.search(
          self._search_ip, self._search_port, self._search_strings)
      self._phue = phue.Bridge(ip=ip_address, username=self._hueAppID)
      self._ready = True
      CloudLog.log(self._component, "Ready.")
    except Exception, e:
      CloudLog.error(self._component, "Error searching for Hue Bridge", e)

  def sendCommand(self, lights, command):
    result = {"completed": False, "request": {}}
    result["request"]["lights"] = lights
    result["request"]["command"] = command
    if self._ready:
      try:
        response = self._phue.set_light(lights, command)
        result["completed"] = True
        result["response"] = response
      except Exception, e:
        CloudLog.error(self._component, "Error calling phue", e)
    else:
      CloudLog.error(self._component, "Device not ready.")
    CloudLog.debug(self._component, json.dumps(result))
    return result

  def status(self):
    result = {"completed": False, "request": {}}
    result["request"]["command"] = "/status"
    if self._ready:
      try:
        response = self._phue.get_api()
        result["completed"] = True
        result["response"] = response
      except Exception, e:
        CloudLog.error(self._component, "Error calling phue", e)
    else:
      CloudLog.error(self._component, "Device not ready.")
    CloudLog.debug(self._component, json.dumps(result))
    return result
