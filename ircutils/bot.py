""" This module contains a class for quickly creating bots. It is the highest
level of abstraction of the IRC protocol available in IRCUtils.

"""
import client
import events


class SimpleBot(client.SimpleClient):
    """ A simple IRC bot to subclass.  When subclassing, make methods in the 
    form of ``on_eventname`` and they will automatically be bound to that 
    event listener. 
    This class inherits from :class:`ircutils.client.SimpleClient`, so be sure 
    to check that documentation to see more of what is available.
    
    """
    def __init__(self, nick):
        client.SimpleClient.__init__(self, nick)
        self._autobind_handlers()
    
    def _autobind_handlers(self):
        """ Looks for "on_<event-name>" methods on the object and automatically
        binds them to the listener for that event.
        
        """
        for listener_name in self.events:
            name = "on_%s" % listener_name
            if hasattr(self, name):
                handler = getattr(self, name).__func__
                self.events[listener_name].add_handler(handler)