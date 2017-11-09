# -*- coding: utf-8 -*-
# vim:tabstop=4:shiftwidth=4:expandtab

import socket
import time

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            data_str = data.decode('utf-8')
            print('received {!r}'.format(data_str))
            if data:
                if data.isdigit():
                    sleep_time = int(data)
                    print('sleep {}(sec)'.format(data_str))
                    time.sleep(sleep_time)
                else:
                    print('{} is not digit'.format(data_str))

                print('sending data back to the client')
                connection.sendall(data)
                break
            else:
                print('no data from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()
