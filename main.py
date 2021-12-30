import asyncio
from asyncio.streams import start_server, StreamReader, StreamWriter, open_connection

import socket
import ipaddress


HOST = "ya.ru"

async def conn_cb(reader: StreamReader, writer: StreamWriter):
    print(writer.get_extra_info('socket'))

    connect_data = await reader.read(1)
    cd = await reader.read(1)
    dst_port = await reader.read(2)
    ip_addr = await reader.read(4)
    user_id = await reader.readuntil(b'\x00')
    print(connect_data)
    print(cd)
    port = int.from_bytes(dst_port, byteorder='big')
    ip: ipaddress.IPv4Address = ipaddress.ip_address(ip_addr)
    print(port)
    print(ip)
    print(user_id)

    # открываем к проксируемому хосту коннект
    dst_reader, dst_writer = await open_connection(host=ip.exploded, port=port)


    # socks ok response
    writer.write(b'\x00')
    writer.write(b'\x5a')
    writer.write(b'\x00\x00')
    writer.write(b'\x00\x00\x00\x00')
    print("end of handshake, wait for curl?")

    # считываем весь запрос
    data = bytearray()
    async for item in reader:
        print(item)
        data += item
    print("test")


    dst_writer.write(data)
    print("test")
    await dst_writer.drain()
    dest_data = await dst_reader.read()

    print(dest_data)
    writer.write(dest_data)
    await writer.drain()
    writer.close()

async def main():
    server = await start_server(conn_cb, port="8888", family=socket.AF_INET, backlog=20)
    await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
