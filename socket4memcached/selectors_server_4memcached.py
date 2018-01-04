# -*- coding: utf-8 -*-
# vim:tabstop=4:shiftwidth=4:expandtab

import logging
import time
import signal
import selectors
import socket
import memcache

logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s',
                    )


class SignalException(Exception):
    def __init__(self, message):
        super(SignalException, self).__init__(message)


def do_exit(sig, stack):
    raise SignalException("Exiting")


mysel = selectors.DefaultSelector()
keep_running = True


def read(connection, mask):
    "Callback for read events"
    global keep_running

    client_address = connection.getpeername()
    print('read({})'.format(client_address))
    data = connection.recv(1024)
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    if data:
        # A readable client socket has data
        print('  received {!r}'.format(data))
        data_str = data.decode()
        value = mc.get(data_str)
        if value is not None:
            sleep_time = 0
            print('sleep {}(sec)'.format(sleep_time))
            time.sleep(sleep_time)
            connection.sendall(value.encode())
        else:
            set_value = '{}_memcached'.format(data_str)
            mc.set(data_str, set_value, time=120)
            sleep_time = 1
            print('sleep {}(sec)'.format(sleep_time))
            time.sleep(sleep_time)
            connection.sendall(set_value.encode())
    else:
        # Interpret empty result as closed connection
        print('  closing')
        mysel.unregister(connection)
        connection.close()
        # Tell the main loop to stop
        keep_running = True


def accept(sock, mask):
    "Callback for new connections"
    new_connection, addr = sock.accept()
    print('accept({})'.format(addr))
    new_connection.setblocking(False)
    mysel.register(new_connection, selectors.EVENT_READ, read)


if __name__ == '__main__':

    # シグナル
    signal.signal(signal.SIGINT, do_exit)
    signal.signal(signal.SIGHUP, do_exit)
    signal.signal(signal.SIGTERM, do_exit)

    server_address = ('localhost', 10000)  # let the kernel assign a port
    print('starting up on {} port {}'.format(*server_address))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(False)
    server.bind(server_address)
    server.listen(5)

    mysel.register(server, selectors.EVENT_READ, accept)
    try:
        while keep_running:
            print('waiting for I/O')
            for key, mask in mysel.select(timeout=1):
                callback = key.data
                callback(key.fileobj, mask)
    except SignalException as e1:
        print(e1, 'Graceful')
    except Exception as e2:
        print(e2)
    finally:
        print('shutting down')
        mysel.close()
