import sys
import socket
import struct
from datetime import datetime, timedelta
import logging

## http://www.globalcache.com/files/docs/API-iTach.pdf

## http://irtek.wikidot.com/

# ('AMXB<-UUID=GlobalCache_000C1E025433><-SDKClass=Utility><-Make=GlobalCache>
#   <-Model=iTachIP2IR><-Revision=710-1005-05><-Pkg_Level=GCPK002>
#   <-Config-URL=http://192.168.1.150><-PCB_PN=025-0028-03><-Status=Ready>\r',
#   ('192.168.1.150', 9131))


class FindiTach:
    def search(self):
        ip = "239.255.250.250"
        port = 9131
        waitTime = 9
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Allow applications reuse the same port
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Join the mulitcast group
        ip_mreq = struct.pack('4sl', socket.inet_aton(ip), socket.INADDR_ANY)
        udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, ip_mreq)

        # Leave the mulitcast group
        # udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, ip_mreq)
        udp_socket.bind((ip, port))
        udp_socket.settimeout(waitTime)
        searchLoop = True
        stopTime = datetime.now() + timedelta(seconds=waitTime*10)
        while searchLoop:
            try:
                sys.stdout.write("*")
                sys.stdout.flush()
                response = udp_socket.recvfrom(1024)
                #print response
                if response[0].find("AMXB<-UUID=GlobalCache_") >= 0 \
                   and response[0].find("<-Model=iTachIP2IR>") >= 0 \
                   and response[0].find("<-Status=Ready>"):
                    print("")
                    return response[1][0]
            except:
                pass
            finally:
                if datetime.now() > stopTime:
                    searchLoop = False
        print('')
        return None
