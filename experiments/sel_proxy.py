import selectors
import socket

import time

sel = selectors.DefaultSelector()

addr = ('ya.ru', 80)

data = b'HEAD / HTTP/1.1\r\nHost: {addr[0]}\r\n\r\n'


def write_callback(sock: socket.socket):
    sock.sendall(data)


s_client: socket.socket

s_client = socket.create_connection(addr)
s_client.setblocking(False)
sel.register(s_client, selectors.EVENT_WRITE | selectors.EVENT_READ)


while True:
    events = sel.select(1)
    if not events:
        print('no events')
    #print(f'events: {events}')
    for k, event_mask in events:
        k: selectors.SelectorKey
        print(f'event_mask: {event_mask}')
        print(f'key: {k}')
        print(f'key_data: {k.data}')
        print(f'k_obj: {k.fileobj}, fd: {k.fd}')
        if event_mask == selectors.EVENT_READ:
            print("event READ")
        if event_mask == selectors.EVENT_WRITE:
            print("event WRITE")
            write_callback(k.fileobj)
        time.sleep(2)
