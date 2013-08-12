import json
import socket
import CloudLog
import HarmonyClient


class Bridge:
  _component = "Harmony.Bridge"
  _ip_address = None
  _port = None
  _uuid = None

  def __init__(self, connection_settings=None):
    CloudLog.log(self._component, "Initializing.")
    if connection_settings is None:
      connection_settings = self._find()
      
    if connection_settings is not None:
      self._ip_address = connection_settings["ip"]
      self._port = connection_settings["port"]
      self._uuid = connection_settings["uuid"]

  def _find(self):
    try:
      search_ip = "192.168.1.255"
      search_port = 5224
      listen_port = 5005
      search_message = '_logitech-reverse-bonjour._tcp.local.\n%d' % listen_port
      # Get my IP address
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.connect(("google.com",80))
      my_ip = s.getsockname()[0]
      s.close()

      # Setup the port to listen for the TCP message on
      listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      listen_sock.settimeout(30)
      listen_sock.bind((my_ip, listen_port))
      listen_sock.listen(1)
      listen_sock.settimeout(None)
      
      # Send the UDP packet to the Harmony Bridge
      send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
      send_sock.sendto(search_message, (search_ip, search_port))

      result = ""
      conn, adr = listen_sock.accept()
      while True:
        data = conn.recv(1024)
        result += data
        if not data:
          break
      conn.close()
      return dict(item.split(":") for item in result.split(";"))
    except Exception, e:
      CloudLog.error(self._component, "Error while searching for Harmony", e)
      return None

  def _getClient(self):
    CloudLog.debug(self._component, "Connecting.")
    try:
      client = HarmonyClient.create_and_connect_client(
                      self._ip_address, self._port, self._uuid)
      CloudLog.debug(self._component, "Connected.")
      return client
    except Exception, e:
      CloudLog.error(self._component, "Error connecting to the Harmony Bridge", e)
      return None

  def _disconnectClient(self, client):
    try:
      if client is not None:
        client.disconnect(send_close=True)
    except Exception, e:
      CloudLog.error(self._component, "Error disconnecting from Harmony Bridge", e)


  def startActivity(self, activity_id):
    result = {"completed": False, "request": {}}
    result["request"]["activity_id"] = activity_id
    client = self._getClient()
    if client:
      try:
        response = client.start_activity(activity_id)
        result["completed"] = True
        result["response"] = response
      except Exception, e:
        CloudLog.error(self._component, "Unable to start activity", e)
        result["error"] = str(e)
      finally:
        self._disconnectClient(client)
    else:
      CloudLog.error(self._component, "No Harmony Bridge available.")
      result["error"] = "No bridge available"
    CloudLog.debug(self._component, json.dumps(result))
    return result

  def currentActivity(self):
    result = {"completed": False, "request": {}}
    result["request"]["command"] = "/currentActivity"
    client = self._getClient()
    if client:
      try:
        response = client.get_current_activity()
        result["completed"] = True
        result["response"] = response
      except Exception, e:
        CloudLog.error(self._component, "Unable to get current activity", e)
        result["error"] = str(e)
      finally:
        self._disconnectClient(client)
    else:
      CloudLog.error(self._component, "No Harmony Bridge available.")
      result["error"] = "No bridge available"
    CloudLog.debug(self._component, json.dumps(result))
    return result

  def getConfig(self):
    result = {"completed": False, "request": {}}
    result["request"]["command"] = "/getConfig"
    client = self._getClient()
    if client:
      try:
        response = self._client.get_config()
        result["completed"] = True
        result["response"] = response
      except Exception, e:
        CloudLog.error(self._component, "Unable to get config", e)
        result["error"] = str(e)
      finally:
        self._disconnectClient(client)
    else:
      CloudLog.error(self._component, "No Harmony Bridge available.")
      result["error"] = "No bridge available"
    CloudLog.debug(self._component, json.dumps(result))
    return result
