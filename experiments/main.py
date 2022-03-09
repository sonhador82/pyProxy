import asyncio
from asyncio.streams import start_server, StreamReader, StreamWriter, open_connection

import struct

import socket
import ipaddress
import logging

logging.basicConfig(level=logging.INFO)


async def client_loop(cl_reader, dst_writer):
    while True:
        # порчитать с клиента буфер
        c_buffer = await cl_reader.read(512)
        print(f'c_buffer: {c_buffer}')
        # закинуть в прокси коннект
        dst_writer.write(c_buffer)


async def client_resp_loop(dst_reader, cl_writer):
    while True:
        s_buffer = await dst_reader.read(512)
        print(f's_buffer: {s_buffer}')
        # закинуть в клиента
        cl_writer.write(s_buffer)



async def conn_cb(cl_reader: StreamReader, cl_writer: StreamWriter):
    print(cl_writer.get_extra_info('socket'))
    connect_data = await cl_reader.read(32)
    data = struct.unpack('3B', connect_data[:3])
    print(f"start hs: {data}")

    resp_handsh = struct.pack('2B', 5, 0)
    print(f"resp start hs: {resp_handsh}")
    cl_writer.write(resp_handsh)


    # read connection info
    req_data = await cl_reader.read(5)
    s_ver, s_cmd, _, s_type, dom_len = struct.unpack('>5B', req_data)
    print(f'ver: {s_ver}, cmd_type: {s_cmd}, s_type: {s_type}, dom_len: {dom_len}')
    domain_name = (await cl_reader.read(dom_len)).decode('utf-8')
    dst_port,  = struct.unpack('>H', await cl_reader.read(2))
    print(f'Connect to {domain_name}:{dst_port}')

    dst_reader, dst_writer = await open_connection(host=domain_name, port=dst_port)

    # send ok, connection opened
    ok_hs_cont = struct.pack('>5B', 5, 0, 0, 3, dom_len)
    cl_writer.write(ok_hs_cont)
    cl_writer.write(domain_name.encode('utf-8'))
    cl_writer.write(struct.pack('>H', dst_port))
    await cl_writer.drain()


    loop = asyncio.get_event_loop()

    print("start")
    task_c = loop.create_task(client_loop(cl_reader, dst_writer))



    # считать с прокси
    task_w = loop.create_task(client_resp_loop(dst_reader, cl_writer))

    await task_c.get_coro()

    dst_writer.close()
    cl_writer.close()
    # считываем весь запрос
    # data = bytearray()
    # async for item in reader:
    #     print(item)
    #     data += item
    # print("test")
    #
    #
    # dst_writer.write(data)
    # print("test")
    # await dst_writer.drain()
    # dest_data = await dst_reader.read()
    #
    # print(dest_data)
    # writer.write(dest_data)
    # await writer.drain()
    # writer.close()

async def main():
    server = await start_server(conn_cb, port="8888", family=socket.AF_INET, backlog=20)
    await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
