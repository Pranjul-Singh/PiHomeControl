import socket
import struct
from datetime import datetime, timedelta
import CloudLog

def search(ip_address, port, strings):
  component = "UDPListener:Search"
  waitTime = 9
  try:
    
    CloudLog.log(component, "Listening on " + ip_address + ":" + str(port))
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Allow applications reuse the same port
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Join the mulitcast group
    ip_mreq = struct.pack('4sl', socket.inet_aton(ip_address), socket.INADDR_ANY)
    udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, ip_mreq)

    # Leave the mulitcast group
    # udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, ip_mreq)
    udp_socket.bind((ip_address, port))
    udp_socket.settimeout(waitTime)
    searchLoop = True
    stopTime = datetime.now() + timedelta(seconds=waitTime*10)
  except Exception, e:
    CloudLog.error(component, "Unable to open multicast socket", e)
    searchLoop = False

  while searchLoop:
    try:
      response = udp_socket.recvfrom(1024)
      result = True
      for item in strings:
        if response[0].find(item) == -1:
          result = False
      if result is True:
        CloudLog.log(component, "Device found on IP: " + response[1][0])
        return response[1][0]
    except socket.timeout, e:
      pass
    except Exception, e:
      CloudLog.error(component, "Error reading from multi-cast socket", e)
    finally:
      if datetime.now() > stopTime:
        searchLoop = False
  CloudLog.error(component, "Device not found (timeout).")
  return None
