"""
    Ident server utilities.
    
    Author:       Evan Fosmark
    Description:  This module contains two distinct ident server 
                  implemtations: `IdentServer` and `FakeIdentServer`. 
                  IdentServer is a fully functional (RFC-1413 compatible) ident 
                  server for Unix machines. FakeIdentServer can be used instead
                  in order to specify your own output data. Typically, this is
                  ideal.
"""
import asyncore, asynchat
import itertools
import os
import socket
import uuid



# Valid response types
USERID = "USERID"
ERROR = "ERROR"

# Valid error responses
INVALID_PORT = "INVALID-PORT"
NO_USER = "NO-USER"
HIDDEN_USER = "HIDDEN-USER"
UNKNOWN_ERROR = "UNKNOWN-ERROR"



def get_operating_system():
    """ Retreives an RFC-1340 compliant name of the operating system. If a name
        doesn't seem to be available, then UNKNOWN is returned instead. This
        function is limited by the possibilities of os.name values.
    """
    os_map = {
        "nt": "WIN32",
        "posix": "UNIX",
        "mac": "MACOS",
        "os2": "OS/2",
        "ce": "WIN32"
        }
    return os_map.get(os.name, "UNKNOWN")



def parse_request(request):
    """ Parse the request line as specified by RFC-1413. This automatically
        converts the two ports to integers and returns a tuple in the form
        of (server_port, client_port).
    """
    server_port, client_port = request.split(",")
    return int(server_port), int(client_port)



def is_valid_port(port):
    """ Checks to see if a port is valid by checking if it is within the range 
        of 1 and 65,535. This is the described range of ports in the TCP
        protocol.
    """
    return 1 <= port <= 65535



def generate_fake_userid():
    """ Create a fake user id. This gets used when FakeIdentServer is being used
        and the userid was initially set to None. It creates a random UUID as
        specified by RFC 4122.
    """
    return str(uuid.uuid4())



def get_user_id(server_port, client_port):
    """ Searches through /proc/net/tcp and /proc/net/tcp6 for a match of the
        server_port and client_port on the machine. This is to be used with
        IdentServer, thus making IdentServer only available on Unix platforms.
    """
    import pwd
    tcp = open("/proc/net/tcp", "r")
    tcp.readline()
    
    try:
        tcp6 = open("/proc/net/tcp6", "r")
        tcp6.readline()
    except:
        tcp6 = []
    
    for line in itertools.chain(tcp, tcp6):
        sections = line.strip().split(" ")
        local_port = int(sections[1].split(":")[1], 16)
        remote_port = int(sections[2].split(":")[1], 16)
        if local_port == server_port and remote_port == client_port:
            uid = int(sections[7])
            return pwd.getpwuid(uid)[0]
    return None



class _IdentChannel(asynchat.async_chat):
    """ An instance of _IdentChannel represents a single request from a client
        to the IdentServer. It isn't designed to be used directly.
    """
    
    def __init__(self, server, sock, addr):
        """ Set up the object by specifying the terminator and initializing the
            input buffer and using the socket passed from the dispatcher. 
            The terminator for the ident protocol is CR+LF.
        """
        asynchat.async_chat.__init__(self, sock)
        self.set_terminator("\r\n")
        self.server = server
        self.ibuffer = []

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
        response = self.handle_request("".join(self.ibuffer))
        self.ibuffer = []
        self.push(":".join(response))
        self.close_when_done()
    
    def handle_request(self, request):
        raise NotImplementedError("handle_request() must be overridden.")



class _FakeIdentChannel(_IdentChannel):
    
    def handle_request(self, request):
        if self.server.response != USERID:
            return request, ERROR, self.server.response
        
        if self.server.userid is not None:
            userid = self.server.userid
        else:
            userid = generate_fake_userid()
        
        if self.server.os is not None:
            sysos = self.server.os
        else:
            sysos = get_operating_system()
        
        return request, USERID, sysos, userid



class _GenuineIdentChannel(_IdentChannel):
    
    def handle_request(self, request):
        if self.server.hidden:
            return request, ERROR, HIDDEN_USER
        try:
            server_port, client_port = parse_request(request)
            
            if is_valid_port(server_port) and is_valid_port(client_port):
                user_id = get_user_id(server_port, client_port)
                if user_id is not None:
                    return request, USERID, self.server.os, user_id
                return request, ERROR, NO_USER
            return request, ERROR, INVALID_PORT
        except Exception as e:
            print e
            return request, ERROR, UNKNOWN_ERROR



class FakeIdentServer(asyncore.dispatcher):
    """ A simple and configurable ident server. The identity protocol is 
        specified in RFC-1413. 
    """
    
    def __init__(self, userid=None, os=None, response=USERID, port=113):
        """ Create the ident server by creating a typical socket and then 
            binding it to the port specified. Note that the standard ident
            port is 113, but since that port is below 1024, you may need
            root access. It is recommended that you instead forward port 113
            to a higher port (such as 1113).
        """
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(("", port))
        self.listen(5)
        self.userid = userid
        self.os = os
        self.response = response

    def handle_accept(self):
        """ Dispatch a request onto an _IdentChannel instance. """
        _FakeIdentChannel(self, *self.accept())
    
    def serve(self):
        """ Begin serving ident requests on the port specified. Instead of
            starting the server individually, you can combine multiple 
            services and call asyncore.loop().
        """
        asyncore.loop(map=self._map)



class IdentServer(asyncore.dispatcher):
    """ A simple and configurable ident server. The identity protocol is 
        specified in RFC-1413. 
    """
    
    def __init__(self, hidden=False, port=113, timeout=120):
        """ Create the ident server by creating a typical socket and then 
            binding it to the port specified. Note that the standard ident
            port is 113, but since that port is below 1024, you may need
            root access. It is recommended that you instead forward port 113
            to a higher port (such as 1113).
        """
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(("", port))
        self.listen(5)
        self.hidden = hidden
        self.timeout = timeout
        self.os = get_operating_system()

    def handle_accept(self):
        """ Dispatch a request onto a _GenuineIdentChannel instance. This is
            to be used """
        _GenuineIdentChannel(self, *self.accept())
    
    def start(self):
        """ Begin serving ident requests on the port specified. Instead of
            starting the server individually, you can combine multiple 
            services and call asyncore.loop().
        """
        asyncore.loop(map=self._map)



class IdentClient(socket.socket):
    """ This is a small and simple ident client for requesting ident information
        from a server. Even though it isn't necessary for an IRC bot to have it,
        I thought it'd be better for the ident module to have it anyhow.
    """
    
    def __init__(self, hostname, port=113):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        self.connect((hostname, port))
    
    def request(self, server_port, local_port):
        self.send("%s,%s\r\n" % (server_port, local_port))
        data = self.recv(4096)
        return data.split(":", 3)[1:]