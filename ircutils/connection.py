"""
    Asynchronous IRC connection.
    
    Author:       Evan Fosmark <me@evanfosmark.com>
    Description:  Manages I/O for a single IRC server and client. This includes
                  reading from the server and pushing a command to the server.
"""
import asyncore, asynchat
import socket

try:
    import ssl
    ssl_available = True
except ImportError:
    ssl_available = False

import protocol
import responses

class Connection(asynchat.async_chat):
    """ This class represents an asynchronous connection with an IRC server. It
        handles all of the dirty work such as maintaining input and output with
        the server as well as automatically handling PING requests.
    """
    
    
    def __init__(self):
        """ Set up the object by specifying the terminator and initializing the
            input buffer and socket. The terminator for the IRC protocol is 
            CR+LF.
        """
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_terminator("\r\n")
        self.ibuffer = []
        self.ping_auto_respond = True
    
    
    def connect(self, hostname, port=None, use_ssl=False, password=None):
        """ Create a connection to the specified host. If a port is given, it'll
            attempt to connect with that. A password may be specified and it'll
            be sent if the IRC server requires one.
        """
        if port is None:
            if use_ssl:
                port = 7000
            else:
                port = 6667
        if use_ssl:
            if not ssl_available:
                raise socket.error("SSL library unavailable.")
            self.socket = ssl.wrap_socket(self.socket)
        asynchat.async_chat.connect(self, (hostname, port))
        if password is not None:
            self.execute("PASS", password)
    
    
    def collect_incoming_data(self, data):
        """ This gets called when data has been received. All it is in charge of
            is appending that data to the input buffer (ibuffer) so that it can
            be used when necessary.
        """
        self.ibuffer.append(data)
    
    
    def found_terminator(self):
        """ When this is activated, it means that the terminator (\r\n) has been
            read. When that happens, we get the input data, clear the buffer,
            and then handle the data collected.
        """
        data = "".join(self.ibuffer)
        self.ibuffer = []
        prefix, command, params = protocol.parse_line(data)
        if command == "PING" and self.ping_auto_respond:
            self.execute("PONG", *params)
        if command.isdigit():
            command = responses.from_digit(command)
        self.handle_line(prefix, command, params)
    
    
    def execute(self, command, *params, **kwargs):
        """ This places an IRC command on the output queue. If the last
            parameter in `params` contains any spaces, it is automatically 
            converted into a  "trailing parameter" by placing a colon on the 
            beginning.
        """
        params = filter(lambda x:x is not None, params)
        if "trailing" in kwargs:
            params = list(params)
            params.append(":%s" % kwargs["trailing"])
        self.push("%s %s\r\n" % (command.upper(), " ".join(params)))
    
    
    def handle_connect(self):
        """ This is overridden so ``asynchat`` won't complain about it not 
            being handled.
        """
        pass
    
    
    def handle_line(self, prefix, command, params):
        """ This gets called when one single line is ready to get handled. It
            is provided in the three main parts of an IRC message as specified
            by RFC-1459. This is primarily designed to be replaced.
        """
        raise NotImplementedError("handle_line() must be overridden.")
    
    
    def start(self):
        """ This causes the connection to begin sending and receiving data. It
            starts a private asyncore loop so if you want to run multiple bots
            on the same loop DO NOT call start() and instead call 
            `asyncore.loop()` after they have been instantiated.
        """
        asyncore.loop(map=self._map)