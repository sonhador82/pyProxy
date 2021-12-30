import asyncio
from asyncio.streams import start_server, StreamReader, StreamWriter, open_connection
import socket


HOST = "ya.ru"

async def conn_cb(reader: StreamReader, writer: StreamWriter):
    reader_data = await reader.read(1000)
    print(reader_data)

    p_reader, p_writer = await open_connection(HOST, 80)
    p_writer.write("GET /\r\n".encode('utf-8'))
    p_writer.write_eof()
    data = await p_reader.readuntil()
    print(data)

    writer.write(data)
    await writer.drain()
    writer.write_eof()

async def main():
    server = await start_server(conn_cb, port="8888", family=socket.AF_INET, backlog=20)
    await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
