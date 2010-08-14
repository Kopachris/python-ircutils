"""
    IRC Bot system.
    
    Author:       Evan Fosmark <me@evanfosmark.com>
    Description:  Contains a class for making a simple IRC bot and one for 
                  making a more advanced IRC bot. The difference being that the
                  advanced one has a built-in means of working with bot commands
                  sent to it. It also auto-generates HELP messages based on
                  command descriptions and docstrings.
"""
import re
import time

import client
import events
from format import bold, underline



class SimpleBot(client.SimpleClient):
    """ A simple IRC bot to subclass.
        When subclassing, make methods in the form of ``on_eventname`` and they
        will automatically be bound to that event listener.
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
