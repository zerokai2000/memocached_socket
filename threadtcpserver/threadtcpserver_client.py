# -*- coding: utf-8 -*-
# vim:tabstop=4:shiftwidth=4:expandtab

import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)
message = sys.argv[1]
message_bi = message.encode('utf-8')

try:

    # Send data
    print('sending {!r}'.format(message))
    sock.sendall(message_bi)

    # Look for the response
    amount_received = 0
    amount_expected = len(message_bi)

    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        print('received {!r}'.format(data.decode('utf-8')))

finally:
    print('closing socket')
    sock.close()
