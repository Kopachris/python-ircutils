""" 
    Events and event listeners.
    
    Author:        Evan Fosmark <me@evanfosmark.com>
    Description:   This module gets used by client.py for event handling and 
                   management.
"""
import bisect
import collections
import re
import traceback

import protocol


class EventDispatcher(object):
    """ The event dispatcher is in charge of three major tasks. (1) Registering
        listeners to the dispatcher, (2) providing a way to interact with the
        listeners, and (3) dispatching events.
    """
    
    def __init__(self):
        self._listeners = {}
    
    def register_listener(self, name, listener):
        self._listeners[name] = listener
    
    def __setitem__(self, name, listener):
        self.register_listener(name, listener)
    
    def __getitem__(self, name):
        return self._listeners[name]
    
    def __iter__(self):
        return iter(self._listeners.keys())
    
    def dispatch(self, client, event):
        """ Notifies all of the listeners that an event is available.
            Any listener which analyses the event and finds it to have what
            the listener is looking for will then activate its event handlers.
        """
        print event.command, event.target, event.source, event.params
        for name, listener in self._listeners.items():
            if listener.handlers != []:
                listener.notify(client, event)



################################################################################
################################################################################
################################################################################


class Event(object):
    """ Represents a standard event.
        An event is made up of:
           command -- The IRC command 
           source -- The person sending the line (nick, server, or None)
           user -- The user id. If one isn't present, this is None.
           host -- The user's hostname. If one isn't present, this is None.
           target -- The target of the event. Either a nick, channel, or None.
           params -- A list of parameters for the event.
    """
    def __init__(self, prefix, command, params):
        self.command = command
        self.source, self.user, self.host = protocol.parse_prefix(prefix)
        if len(params) > 0:
            self.target = params[0]
            self.params = params[1:]
        else:
            self.target = None
            self.params = []


class CTCPEvent(Event):
    def __init__(self):
        self.source = None
        self.target = None
        self.command = None
        self.params = []


class MessageEvent(Event):
    """ Represents a standard message received.
        The message event contains:
           message -- The text of the message
           target -- The target of the event. Either a nick or channel.
           source -- The source of the message. Either a nick or service.
           command -- The command, either PRIVMSG or NOTICE.
    """
    def __init__(self, base_event):
        self.base_event = base_event
        self.message = base_event.params[-1]
        self.target = base_event.target
        self.source = base_event.source
        self.command = base_event.command


class ReplyEvent(Event):
    pass


class NameReplyEvent(Event):
    def __init__(self):
        self.channel = None
        self.name_list = []


class WhoisEvent(Event):
    def __init__(self):
        self.nick = None
        self.user = None
        self.host = None
        self.real_name = None
        self.channels = []
        self.server = None


################################################################################
####### listeners and helper code ##############################################
################################################################################

class Priority(object):
    """ The priority object is used to set an element at a specific end of the
        sorted list of listeners. For instance, to make something low priotity,
        one would use Priority.LOW.
    """
    def __init__(self, comparison):
        self.comparison = comparison
    
    def __cmp__(self, other):
        return self.comparison
    
    def __eq__(self, other):
        if isinstance(other, Priority):
            return self.comparison == other.comparison
        else:
            return False

Priority.HIGH = Priority(1)
Priority.NORMAL = Priority(0)
Priority.LOW = Priority(-1)



class HaltHandling(Exception):
    """ This is a special exception as when it gets thrown in a handler 
        callback, it will halt any other callbacks to be run. This, combined 
        with setting a handler to Priority.HIGH is exceptional for preventing
        further handlers from being run.
    """
    pass



class EventListener(object):
    """ This class is a simple event listener designed to be subclassed. Each
        event listener is in charge of activating its handlers. 
    """
    
    def __init__(self):
        """ Sets up a list to be used by the `insort` method of the `bisect`
            module to keep the handlers ordered by priority.
        """
        self.handlers = []
    
    def add_handler(self, handler, priority=Priority.NORMAL):
        """ Add a handler to the event listener. It will be called when the 
            listener decides it's time. It will place it in order depending
            on the priority specified. The default is Priority.NORMAL. It can
            be any number you wish or Priority.LOW, Priority.NORMAL, or
            Priority.HIGH.
        """
        bisect.insort(self.handlers, (priority, handler))
        return handler
    
    def remove_handler(self, handler):
        """ This removes all handlers that are equal to the ``handler`` which
            are bound to the event listener. This isn't too inefficient since
            it is O(n^2).
        """
        for p, l in self.handlers:
            if l == handler:
                self.handlers.remove((p,l))
    
    def activate_handlers(self, *args):
        """ This activates each handler that's bound to the listener. It works
            in order, so handlers with a higher priority will be activated 
            before all others. The ``args`` sent to this will be sent to each
            handler. It's a good idea to always make sure to send in the client
            and the event.
        """
        for p, handler in self.handlers:
            try:
                handler(*args)
            except HaltHandling:
                break
            except StandardError, ex:
                traceback.print_exc(ex)
                self.handlers.remove((p, handler))
    
    def notify(self, client, event):
        """ This is to be overridden when subclassed. It gets called after each
            event generated by the system. If the event listener decides to, it
            should run its handlers from here.
        """
        raise NotImplementedError("This must be overridden.")


class AnyListener(EventListener):
    def notify(self, client, event):
        self.activate_handlers(client, event)

class WelcomeListener(EventListener):
    def notify(self, client, event):
        if event.command == "RPL_WELCOME":
            self.activate_handlers(client, event)

class MessageListener(EventListener):
    def notify(self, client, event):
        if event.command in ["PRIVMSG", "NOTICE"]:
            self.activate_handlers(client, MessageEvent(event))

class PrivateMessageListener(MessageListener):
    def notify(self, client, event):
        if event.command == "PRIVMSG":
            if not protocol.is_channel(event.target):
                self.activate_handlers(client, MessageEvent(event))

class ChannelMessageListener(MessageListener):
    def notify(self, client, event):
        if event.command == "PRIVMSG":
            if protocol.is_channel(event.target):
                self.activate_handlers(client, MessageEvent(event))

class NoticeListener(MessageListener):
    def notify(self, client, event):
        if event.command == "NOTICE":
            self.activate_handlers(client, MessageEvent(event))

class PrivateNoticeListener(NoticeListener):
    def notify(self, client, event):
        if event.command == "NOTICE":
            if not protocol.is_channel(event.target):
                self.activate_handlers(client, MessageEvent(event))

class ChannelNoticeListener(NoticeListener):
    def notify(self, client, event):
        if event.command == "NOTICE":
            if protocol.is_channel(event.target):
                self.activate_handlers(client, MessageEvent(event))

class NickChangeListener(EventListener):
    def notify(self, client, event):
        if event.command == "NICK":
            self.activate_handlers(client, event)

class PingListener(EventListener):
    def notify(self, client, event):
        if event.command == "PING":
            self.activate_handlers(client, event)

class InviteListener(EventListener):
    def notify(self, client, event):
        if event.command == "INVITE":
            self.activate_handlers(client, event)

class KickListener(EventListener):
    def notify(self, client, event):
        if event.command == "KICK":
            self.activate_handlers(client, event)

class JoinListener(EventListener):
    def notify(self, client, event):
        if event.command == "JOIN":
            self.activate_handlers(client, event)

class QuitListener(EventListener):
    def notify(self, client, event):
        if event.command == "QUIT":
            self.activate_handlers(client, event)

class PartListener(EventListener):
    def notify(self, client, event):
        if event.command == "PART":
            self.activate_handlers(client, event)

class ErrorListener(EventListener):
    def notify(self, client, event):
        if event.command == "ERROR":
            self.activate_handlers(client, event)

class UnknownListener(EventListener):
    def notify(self, client, event):
        self.activate_handlers(client, event)



standard = {
    "any": AnyListener,
    "welcome": WelcomeListener,
    "message": MessageListener,
    "channel_message": ChannelMessageListener,
    "private_message": PrivateMessageListener,
    "channel_notice": ChannelNoticeListener,
    "private_notice": PrivateNoticeListener,
    "nick_change": NickChangeListener,
    "ping": PingListener,
    "invite": InviteListener,
    "kick": KickListener,
    "join": JoinListener,
    "quit": QuitListener,
    "part": PartListener,
    "error": ErrorListener,
    "unknown": UnknownListener
    }


################################################################################
################################################################################
################################################################################


class CTCPListener(EventListener):
    def notify(self, client, event):
        if event.command.startswith("CTCP_"):
            self.activate_handlers(client, event)

class CTCPActionListener(CTCPListener):
    def notify(self, client, event):
        if event.command == "CTCP_ACTION":
            self.activate_handlers(client, event)

class CTCPUserInfoListener(CTCPListener):
    def notify(self, client, event):
        if event.command == "CTCP_USERINFO":
            self.activate_handlers(client, event)

class CTCPClientInfoListener(CTCPListener):
    def notify(self, client, event):
        return event.command == "CTCP_CLIENTINFO"

class CTCPVersionListener(CTCPListener):
    def notify(self, client, event):
        if event.command == "CTCP_VERSION":
            self.activate_handlers(client, event)

class CTCPPingListener(CTCPListener):
    def notify(self, client, event):
        if event.command == "CTCP_PING":
            self.activate_handlers(client, event)

class CTCPErrorListener(CTCPListener):
    def notify(self, client, event):
        if event.command == "CTCP_ERROR":
            self.activate_handlers(client, event)

class CTCPTimeListener(CTCPListener):
    def notify(self, client, event):
        if event.command == "CTCP_TIME":
            self.activate_handlers(client, event)

class DCCListener(CTCPListener):
    def notify(self, client, event):
        if event.command.startswith("DCC_"):
            self.activate_handlers(client, event)

class DCCConnectListener(DCCListener):
    def notify(self, client, event):
        if event.command == "DCC_CONNECT":
            self.activate_handlers(client, event)

class DCCDisconnectListener(DCCListener):
    def notify(self, client, event):
        if event.command == "DCC_DISCONNECT":
            self.activate_handlers(client, event)



ctcp = {
    "ctcp": CTCPListener,
    "ctcp_action": CTCPActionListener,
    "ctcp_userinfo": CTCPUserInfoListener,
    "ctcp_clientinfo": CTCPClientInfoListener,
    "ctcp_version": CTCPVersionListener,
    "ctcp_ping": CTCPPingListener,
    "ctcp_error": CTCPErrorListener,
    "ctcp_time": CTCPTimeListener,
    "dcc": DCCListener,
    "dcc_connect": DCCConnectListener,
    "dcc_disconnect": DCCDisconnectListener
    }


################################################################################
################################################################################
################################################################################



class ReplyListener(EventListener):
    def notify(self, client, event):
        if event.command.startswith("RPL_"):
            self.activate_handlers(client, event)


class NameReplyListener(ReplyListener):
    name_prefix = re.compile(r"^[\+%@&~]")
    
    def __init__(self):
        ReplyListener.__init__(self)
        self._name_lists = collections.defaultdict(NameReplyEvent)
    
    def notify(self, client, event):
        if event.command == "RPL_NAMREPLY":
            channel = event.params[1]
            names = event.params[2].strip().split(" ")
            names = map(lambda n:self.name_prefix.sub(n, ""), names)
            self._name_lists[channel].name_list.extend(names)
        elif event.command == "RPL_ENDOFNAMES":
            name_event = self._name_lists[event.params[1]]
            name_event.channel = event.params[1]
            self.activate_handlers(client, name_event)
            del self._name_lists[event.params[1]]


class WhoisListener(ReplyListener):
    """ http://tools.ietf.org/html/rfc1459#section-4.5.2
    
    """
    def __init__(self):
        ReplyListener.__init__(self)
        self._whois_replies = collections.defaultdict(WhoisEvent)
    
    def notify(self, client, event):
        if event.command == "RPL_WHOISUSER":
            """<nick> <user> <host> * :<real name>"""
            reply = self._whois_replies[event.params[1]]
            reply.nick = event.params[0]
            reply.user = event.params[1] # TODO: get rid of the n= part
            reply.host = event.params[2]
            reply.real_name = event.params[5]
        elif event.command == "RPL_WHOISCHANNELS":
            channels = event.params[2].strip().split()
            self._whois_replies[event.params[1]].channels.extend(channels)
        #elif event.command == "RPL_WHOISSERVER":
        #    self._whois_replies[event.params[1]].server = event.params[2]
        #elif event.command == "RPL_WHOISIDLE":
        #    self._whois_replies[event.params[1]].idle = event.params[1]
        #elif event.command == "RPL_WHOISOPERATOR":
        #    self._whois_replies[event.params[1]].is_operator = True
        #elif event.command == "RPL_WHOISSPECIAL":
        #    self._whois_replies[event.params[1]].special.append(event.params[2])
        elif event.command == "RPL_ENDOFWHOIS":
            self.activate_handlers(client, self._whois_replies[event.params[1]])
            del self._whois_replies[event.params[1]]


class ErrorReplyListener(ReplyListener):
    def notify(self, client, event):
        if event.command.startswith("ERR_"):
            self.activate_handlers(client, event)


replies = {
    "reply": ReplyListener,
    "name_reply": NameReplyListener,
    "whois_reply": WhoisListener,
    "error_reply": ErrorReplyListener,
    }