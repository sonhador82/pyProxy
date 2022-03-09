import ipaddress
import socket
import struct
import asyncio
import logging

logging.basicConfig(level=logging.INFO)


async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")

    print(f"Send: {message!r}")
    writer.write(data)
    await writer.drain()

    print("Close the connection")
    writer.close()



SOCKS_VER = 0x05
NOAUTH = 0x00
USERPASSAUTH = 0x02

SOCKS_ATYPE_IP = 0x01
SOCKS_ATYPE_DOMAIN = 0x02
SOCKS_CMD_CONNECT = 0x01
SOCKS_RESP_OK = 0x00
USERNAME='sonhador'
PASSWORD = 'secret'


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    logging.info(f'reader: {reader}, writer: {writer}')
    data = await reader.read(2)
    socks_ver, num_methods = struct.unpack('>2B', data)
    data = await reader.read(num_methods)
    auth_methods = struct.unpack(f'>{num_methods}B', data)
    if USERPASSAUTH not in auth_methods:
        logging.error('error authentication client')
        writer.close()
    # send resp
    logging.info('send auth response to client')
    writer.write(struct.pack('>2B', SOCKS_VER, USERPASSAUTH))

    # read client auth
    data = await reader.read(2)
    _, name_len = struct.unpack('>2B', data)
    data = await reader.read(name_len)
    username = data.decode()
    pass_len = await reader.read(1)
    data = await reader.read(ord(pass_len))
    password = data.decode()
    print(f'user:{username}, pass:{password},')
    if username != USERNAME and password != PASSWORD:
        logging.error('Socks auth failed')
        err_resp = struct.pack('>2B', 0x01, 0x01)
        writer.write(err_resp)
        writer.close()
    ok_auth_resp = struct.pack('>2B', 0x01, 0x00)
    writer.write(ok_auth_resp)

    # client request to remote
    data = await reader.read(4)
    s_ver, s_cmd, _rsv, s_atype = struct.unpack('>4B', data)
    if s_cmd != SOCKS_CMD_CONNECT and s_atype != SOCKS_ATYPE_IP:
        logging.error(f'some socks cmd error: {s_cmd}, {s_atype}')
        writer.close()

    logging.info('request to ip connect')
    data = await reader.read(4)
    remote_ip = socket.inet_ntoa(data)
    data = await reader.read(2)
    remote_port, = struct.unpack('>H', data)
    logging.info(f'remote address: {remote_ip}:{remote_port}')

    # make connection to remote
    rem_reader, rem_writer = await asyncio.open_connection(remote_ip, remote_port)

    # response ok to socks client
    local_ip, local_port = rem_writer.get_extra_info('sockname')
    print(local_ip, local_port)
    ok_conn_resp = struct.pack('>4B', SOCKS_VER, SOCKS_RESP_OK, 0x00, s_atype)
    writer.write(ok_conn_resp)
    writer.write(ipaddress.IPv4Address(local_ip).packed)
    writer.write(struct.pack('>H', local_port))

    task1 = asyncio.create_task(exchange_loop_client(reader, rem_writer))
    print('after task1')
    task2 = asyncio.create_task(exchange_loop_remote(rem_reader, writer))


async def exchange_loop_remote(remote_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter):
    while True:
        data = await remote_reader.read(1024)
        if data == b'':
            break
        print(f'remote reader data {data}')
        client_writer.write(data)


async def exchange_loop_client(client_reader: asyncio.StreamReader, remote_writer: asyncio.StreamWriter):
    while True:
        data = await client_reader.read(1024)
        print(f'client reader data: {data}')
        remote_writer.write(data)


async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 9000)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())
