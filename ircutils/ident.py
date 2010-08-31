""" This module contains a quick ident server implentation: 
``IdentServer``. IdentServer is a functional ident server that returns fake data
and can be used with IRC bots or clients. This is useful for two reasons; it
speeds up connection time, and some servers require an ident response for 
security purposes.

"""
import asyncore, asynchat
import os
import socket
import uuid


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
    
    def __init__(self, userid, sock, addr):
        """ Set up the object by specifying the terminator and initializing the
        input buffer and using the socket passed from the dispatcher. The 
        terminator for the ident protocol is CR+LF.
        """
        asynchat.async_chat.__init__(self, sock)
        self.set_terminator("\r\n")
        self.userid = userid
        self.collect_incoming_data = self._collect_incoming_data

    def found_terminator(self):
        """ When this is activated, it means that the terminator (\r\n) has been
        read. When that happens, we get the input data, clear the buffer,
        and then handle the data collected.
        """
        request = "".join(self.incoming)
        sysos = get_operating_system()
        
        response = (request, "USERID", sysos, self.userid)
        
        self.incoming = []
        self.push(":".join(response))
        self.close_when_done()




class IdentServer(asyncore.dispatcher):
    """ A quick and easy ident server. In order to run the ident server inline
    with an IRC bot or client, be sure to use ``start_all()`` instead of 
    calling the ``start()`` method.
    
    """
    def __init__(self, port=113, userid=None):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(("", port))
        self.listen(5)
        self.userid = userid or generate_fake_userid()
        
    def handle_accept(self):
        """ Dispatch a request onto an _IdentChannel instance. """
        _IdentChannel(self.userid, *self.accept())
        
    def start(self):
        """ Begin serving ident requests on the port specified. """
        asyncore.loop(map=self._map)