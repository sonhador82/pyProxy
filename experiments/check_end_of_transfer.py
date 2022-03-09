import asyncio
from asyncio.streams import start_server, StreamReader, StreamWriter, open_connection


HOST = "ifconfig.me"
PORT = "80"


async def main():
    print("hello")
    reader, writer = await open_connection(HOST, PORT)
    data = f'HEAD / HTTP/1.1\r\nHost: {HOST}\r\n\r\n'
    writer.write(data.encode('latin-1'))

    count = 0
    while True:
        chunk = await reader.readline()
        print(f'chunk: {chunk}')
        if not chunk:
            count += 1
            if count > 10:
                break
    print("before close")
    writer.close()

    # writer.write()
    # print(reader, writer)
# > HEAD / HTTP/1.1
# > Host: ya.ru
# > User-Agent: curl/7.74.0
# > Accept: */*


if __name__ == '__main__':
    asyncio.run(main())

