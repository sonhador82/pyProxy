import asyncio
import socket
from asyncio import AbstractEventLoop
import struct


async def hello_hs(conn: socket, loop: AbstractEventLoop) -> None:
    conn_data = await loop.sock_recv(conn, 2)
    proxy_ver, num_of_authz = struct.unpack('2B', conn_data)
    print(f'Proxy version: {proxy_ver}, num of authz: {num_of_authz}')
    authz_methods = await loop.sock_recv(conn, num_of_authz)
    print(authz_methods)
    no_auth_method = 0
    resp_handsh = struct.pack('2B', 5, no_auth_method)
    print(f"resp start hs: {resp_handsh}")
    await loop.sock_sendall(conn, resp_handsh)


async def exchange_client_loop(client: socket.socket, rem_writer: asyncio.StreamWriter):
    print(f'ex client loop: socket: {client}')

    while True:
        client.setblocking(True)
        data = client.recv(1024)
        client.setblocking(False)
        print(f'client data: {data}')
        rem_writer.write(data)
        await rem_writer.drain()
        print(f'end of wirte client data')

async def exchange_remote_loop(client: socket.socket, rem_reader: asyncio.StreamReader):
    print(f'ex rem loop')
    while True:
        print('remo in loop')
        data = await rem_reader.read(1024)
        print(f'remote data: {data}')
        client.setblocking(True)
        if client.send(data) <= 0:
            break
        client.setblocking(False)

async def req_msg(conn: socket, loop: AbstractEventLoop) -> None:
    req_data = await loop.sock_recv(conn, 5)
    s_ver, s_cmd, _, s_type, dom_len = struct.unpack('>5B', req_data)
    print(f'ver: {s_ver}, cmd_type: {s_cmd}, s_type: {s_type}, dom_len: {dom_len}')
    domain_name = (await loop.sock_recv(conn, dom_len)).decode('utf-8')
    dst_port,  = struct.unpack('>H', await loop.sock_recv(conn, 2))
    print(f'Connect to {domain_name}:{dst_port}')

    remote_reader, remote_writer = await make_remote_tcp_conn_to(domain_name, dst_port)
    proxy_ip, proxy_port = remote_writer.get_extra_info('sockname')
    print(f'socket proxy ip: {proxy_ip}, proxy_port: {proxy_port}')
    # send ok, connection opened
    resp_ok = 0
    resp_addr_type = 0x1
    ok_hs_cont = struct.pack('>4B', 5, resp_ok, 0, resp_addr_type)
    conn.sendall(ok_hs_cont)
    conn.sendall(socket.inet_aton(proxy_ip))
    conn.sendall(struct.pack('>I', proxy_port))
    print("end of hs")
    task1 = asyncio.create_task(exchange_client_loop(conn, remote_writer))
    task2 = asyncio.create_task(exchange_remote_loop(conn, remote_reader))
    print("after tasks")

#    result = await asyncio.gather(task1, task2)
    print("after")


async def make_remote_tcp_conn_to(host, port) -> (asyncio.StreamReader, asyncio.StreamWriter):
    print(f'make conn to {host}:{port}')
    reader, writer = await asyncio.open_connection(host, port)
    return reader, writer





async def echo(connection: socket, loop: AbstractEventLoop) -> None:
    await hello_hs(connection, loop)
    await req_msg(connection, loop)
    print("end of echo")

async def listen_for_connection(server_socket: socket, loop: AbstractEventLoop):
    while True:
        connection, address = await loop.sock_accept(server_socket)
        connection.setblocking(False)
        print(f'Go a connection from {address}')
        asyncio.create_task(echo(connection, loop))


async def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = ('127.0.0.1', 9000)
    server_socket.setblocking(False)
    server_socket.bind(server_address)
    server_socket.listen()

    await listen_for_connection(server_socket, asyncio.get_event_loop())

asyncio.run(main())
