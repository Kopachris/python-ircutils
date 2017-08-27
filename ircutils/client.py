"""Implement SimpleClient, a base class for more complicated clients"""

import asyncio

from . import connection


class SimpleClient:
    def __init__(self, host: str = '', port: int = 0, ssl: bool = False, nick: str = '', user: str = ''):
        self.host = host
        self.port = port
        self.ssl = ssl
        self.nick = nick
        self.user = user

        self.loop = asyncio.get_event_loop()

        self.connection = connection.ClientConnection(host, port, ssl)

    async def connect(self):
        await self.connection.connect()

    def run(self):
        self.loop.create_task(self.connect())
        self.loop.run_forever()
        self.loop.close()