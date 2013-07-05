import socket
import logging
import HarmonyClient


_harmonyHub = None

def findHub():
  global _harmonyHub

  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("google.com",80))
    MY_IP = s.getsockname()[0]
    s.close()
    LISTEN_PORT = 5005
    print MY_IP
     
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_sock.bind((MY_IP, LISTEN_PORT))
    listen_sock.listen(1)

    BROADCAST_IP = '192.168.1.255'
    BROADCAST_PORT = 5224
    MESSAGE = '_logitech-reverse-bonjour._tcp.local.\n%d' % LISTEN_PORT
     
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    send_sock.sendto(MESSAGE, (BROADCAST_IP, BROADCAST_PORT))
     
    result = ""
    conn, addr = listen_sock.accept()
    while True:
      data = conn.recv(1024)
      result += data
      if not data:
        break
    conn.close()
    result = dict(item.split(":") for item in result.split(";"))
    _harmonyHub = result
  except Exception, e:
    logging.error("Unable to find Harmony Hub: " + str(e))
    _harmonyHub = None
    result = None
  return result


def startActivity(activityID):
  global _harmonyHub

  client = HarmonyClient.create_and_connect_client(_harmonyHub['ip'],
                                                   _harmonyHub['port'],
                                                   _harmonyHub['uuid'])
  try:
    result = client.start_activity(activityID)
  except:
    result = None
  client.disconnect(send_close=True)
  return result


def sendCommand(command):
  pass


def getCurrentActivity():
  global _harmonyHub

  client = HarmonyClient.create_and_connect_client(_harmonyHub['ip'],
                                                   _harmonyHub['port'],
                                                   _harmonyHub['uuid'])
  try:
    result = client.get_current_activity()
  except:
    result = None
  client.disconnect(send_close=True)
  return result


def getConfig():
  global _harmonyHub

  client = HarmonyClient.create_and_connect_client(_harmonyHub['ip'],
                                                   _harmonyHub['port'],
                                                   _harmonyHub['uuid'])
  try:
    result = client.get_config()
  except:
    result = None
  client.disconnect(send_close=True)
  return result


def turnOff():
  global _harmonyHub

  client = HarmonyClient.create_and_connect_client(_harmonyHub['ip'],
                                                   _harmonyHub['port'],
                                                   _harmonyHub['uuid'])
  try:
    result = client.turn_off()
  except:
    result = None
  client.disconnect(send_close=True)
  return result
