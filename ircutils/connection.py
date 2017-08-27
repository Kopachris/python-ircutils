"""Implement Client and Server connection classes. Connections provide read and
write methods as well as abstracting the underlying streams. Uses
`asyncio.open_connection()`."""

import asyncio
import ssl


class BaseConnection:
    def __init__(self):
        pass

    def read(self):
        raise NotImplementedError()

    def write(self, data):
        raise NotImplementedError()


class ClientConnection:

    def __init__(self, host: str, port: int, ssl: bool = False, connect: bool = False):
        self.loop = asyncio.get_event_loop()

        self.host = host
        self.port = port
        self.ssl = ssl
        self.ssl_context = None

        self.reader = None
        self.writer = None

        if connect:
            self.connect()

    def connect(self):
        """Establish a streaming connection and set the instance's reader and
        writer
        """

        if self.ssl:
            if not self.ssl_context:
                # create a default ssl context for the client
                ssl_context = ssl.SSLContext()
            else:
                # use existing ssl context
                ssl_context = self.ssl_context
        else:
            # pass False to open_connection(), no ssl
            ssl_context = False

        self.reader, self.writer = asyncio.open_connection(self.host,
                                                           self.port,
                                                           ssl=ssl_context,
                                                           loop=self.loop,
                                                           )


class ServerConnection:
    pass