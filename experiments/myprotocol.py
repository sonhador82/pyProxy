import asyncio
from asyncio import transports
from typing import Optional


class MyProtocolo(asyncio.Protocol):
    def data_received(self, data: bytes) -> None:
        print(f'data recieved: {data}')

    def eof_received(self) -> Optional[bool]:
        print('eof recieved')

    def connection_made(self, transport: transports.BaseTransport) -> None:
        print(f'connection made: {transport}')

    def connection_lost(self, exc: Optional[Exception]) -> None:
        print(f'connection lost')

    def pause_writing(self) -> None:
        print(f'pause writing')

    def resume_writing(self) -> None:
        print(f'resume writing')




async def main():
    print("main func")
    loop = asyncio.get_event_loop()
    transport, proto = await loop.create_connection(MyProtocolo, 'ya.ru', 443)
    sock = transport.get_extra_info('socket')
    print(sock)
    print(transport)
    print(proto)



if __name__ == '__main__':
    asyncio.run(main())
