import socket
 
MY_IP = '192.168.1.6'
LISTEN_PORT = 5005
 
listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_sock.bind((MY_IP, LISTEN_PORT))
listen_sock.listen(1)
print 'started listening'
 
BROADCAST_IP = '192.168.1.255'
BROADCAST_PORT = 5224
MESSAGE = '_logitech-reverse-bonjour._tcp.local.\n%d' % LISTEN_PORT
 
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
send_sock.sendto(MESSAGE, (BROADCAST_IP, BROADCAST_PORT))
print 'sent'
 
conn, addr = listen_sock.accept()
while True:
  data = conn.recv(1024)
  print 'received data size', len(data)
  print '======'
  print data,
  print '\n======'
  if not data:
    break
conn.close()