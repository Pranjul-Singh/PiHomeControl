import sys
import socket
import struct
from datetime import datetime, timedelta
import phue
import logging


class FindHub():
    def search(self):
        ip = ""
        port = 1900
        waitTime = 9
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Allow applications reuse the same port
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Join the mulitcast group
        ip_mreq = struct.pack('4sl', socket.inet_aton("239.255.255.250"), socket.INADDR_ANY)
        udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, ip_mreq)

        # Leave the mulitcast group
        # udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, ip_mreq)
        udp_socket.bind((ip, port))
        udp_socket.settimeout(waitTime)
        searchLoop = True
        stopTime = datetime.now() + timedelta(seconds=waitTime*10)
        hubIP = None
        while searchLoop:
            try:
                sys.stdout.write("*")
                sys.stdout.flush()
                response = udp_socket.recvfrom(1024)
                #print response
                if response[0].find("NOTIFY * HTTP/1.1") >= 0 \
                   and response[0].find(":80/description.xml") >= 0:
                    hub = self.testHub(response[1][0])
                    if hub is not None:
                        return hub
            except:
                pass
            finally:
                if datetime.now() > stopTime:
                    searchLoop = False
        print('')
        return None

    def testHub(self, ip_address):
        try:
            hub = phue.Bridge(ip=ip_address, username="9075e416a7d67c2f6c7d9386dff2e591")
            return hub
        except:
            return None
