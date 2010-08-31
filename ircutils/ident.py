""" This module contains two distinct ident server implemtations: 
``IdentServer`` and ``FakeIdentServer``. IdentServer is a fully functional 
(RFC-1413 compatible) ident server for Unix machines. FakeIdentServer can be 
used instead in order to specify your own output data. Typically, this is ideal.

"""
import asyncore, asynchat
import os


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



def generate_fake_userid():
    """ Create a fake user id. This gets used when FakeIdentServer is being used
    and the userid was initially set to None. It creates a random UUID as
    specified by RFC 4122.
    """
    return str(uuid.uuid4())



class _IdentChannel(asynchat.async_chat):
    """ An instance of _IdentChannel represents a single request from a client
    to the IdentServer. It isn't designed to be used directly.
    """
    
    def __init__(self, server, sock, addr):
        """ Set up the object by specifying the terminator and initializing the
        input buffer and using the socket passed from the dispatcher. The 
        terminator for the ident protocol is CR+LF.
        """
        asynchat.async_chat.__init__(self, sock)
        self.set_terminator("\r\n")
        self.server = server

    def found_terminator(self):
        """ When this is activated, it means that the terminator (\r\n) has been
        read. When that happens, we get the input data, clear the buffer,
        and then handle the data collected.
        """
        response = self.handle_request("".join(self.incoming))
        self.incoming = []
        self.push(":".join(response))
        self.close_when_done()
    
    def handle_request(self, request):
        if self.server.response != USERID:
            return request, ERROR, self.server.response
        
        sysos = get_operating_system()
        userid = generate_fake_userid()
        
        return request, "USERID", sysos, userid



class IdentServer(asyncore.dispatcher):
    """ A simple and configurable ident server. """
    
    def __init__(self, port=113):
        """ Create the ident server by creating a typical socket and then 
        binding it to the port specified. 
       
        """
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(("", port))
        self.listen(5)

    def handle_accept(self):
        """ Dispatch a request onto an _IdentChannel instance. """
        _IdentChannel(self, *self.accept())
    
    def start(self):
        """ Begin serving ident requests on the port specified. """
        asyncore.loop(map=self._map)