""" This module contains a class for quickly creating bots. It is the highest
level of abstraction of the IRC protocol available in ``ircutils``.

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

    def register_listener(self, event_name, listener):
        """ Same as :func:`ircutils.client.SimpleClient.register_listener` 
        execpt that if there is a handler in the bot already, it auto-binds it
        to the listener.
        """
        self.events.register_listener(event_name, listener)
        handler_name = "on_{0}".format(event_name)
        if hasattr(self, handler_name):
            handler = getattr(self, handler_name).__func__
            self.events[event_name].add_handler(handler)


class _TestBot(SimpleBot):
    """ A bot for debugging. Designed to be subclassed to building test bots.
    
    """
    def __init__(self, nick):
        SimpleBot.__init__(self, nick)
        self["any"].add_handler(self.print_line)
        self.verbose = True
    
    def print_line(self, client, event):
        kwds = {
            "cmd": event.command,
            "src": event.source,
            "tgt": event.target,
            "params": event.params
            }
        if self.verbose:
            print "[{cmd}] s={src!r} t={tgt!r} p={params}".format(**kwds)