""" This module contains a class for quickly creating bots. It is the highest
level of abstraction of the IRC protocol available in IRCUtils.

"""
try:
    import threading
except ImportError:
    import dummy_threading as threading

import client
import events


def threaded(func):
    """ Decorator that causes a callable to become threaded. This is useful to 
    place on event handlers if they are highly CPU-bound.
    """
    def wrap(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
    return wrap 


class SimpleBot(client.SimpleClient):
    """ A simple IRC bot to subclass.  When subclassing, make methods in the 
    form of ``on_eventname`` and they will automatically be bound to that 
    event listener. 
    This class inherits from :class:`ircutils.client.SimpleClient`, so be sure 
    to check that documentation to see more of what is available.
    
    """
    
    def _autobind_handlers(self):
        """ Looks for "on_<event-name>" methods on the object and automatically
        binds them to the listener for that event.
        
        """
        for listener_name in self.events:
            name = "on_%s" % listener_name
            if hasattr(self, name):
                handler = getattr(self, name).__func__
                self.events[listener_name].add_handler(handler)
    
    def start(self):
        self._autobind_handlers()
        client.SimpleClient.start(self)


class _TestBot(SimpleBot):
    """ A bot for debugging. Designed to be subclassed to building test bots.
    
    """
    def __init__(self, nick):
        SimpleBot.__init__(self, nick)
        self.verbose = True
    
    def on_any(self, event):
        kwds = {
            "cmd": event.command,
            "src": event.source,
            "tgt": event.target,
            "params": event.params
            }
        if self.verbose:
            print "[{cmd}] s={src!r} t={tgt!r} p={params}".format(**kwds)