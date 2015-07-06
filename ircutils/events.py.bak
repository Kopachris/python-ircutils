""" This module gets used by :class:`ircutils.client.SimpleClient` and
:class:`ircutils.bot.SimpleBot`  for event handling and management.

Each line sent from the IRC server represents its own event. This information
is parsed to fill in the values for the event object. In some cases, these
single-line events are combined together to build more complex events that span
multiple lines of data from the server.  This information
is parsed to fill in the values for the event object. 
"""
import bisect
import collections
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
        """ Adds a listener to the dispatcher. """
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
        for name, listener in self._listeners.items():
            if listener.handlers != []:
                listener.notify(client, event)



# ------------------------------------------------------------------------------
# > BEGIN EVENT OBJECTS 
# ------------------------------------------------------------------------------
#


class Event(object):
    pass


class ConnectionEvent(Event):
    """ Handles events for connecting and disconnecting. Currently, the only useful data in
    the event object is the command. It will either be CONN_CONNECT or CONN_DISCONNECT.
    """
    def __init__(self, command):
        self.command = command
        self.source = None
        self.target = None
        self.params = []


class StandardEvent(Event):
    """ Represents a standard event. """
    def __init__(self, prefix, command, params):
        self.command = command
        self.prefix = prefix
        self.source, self.user, self.host = protocol.parse_prefix(prefix)
        if len(params) > 0:
            if command not in protocol.commands_with_no_target:
                self.target = params[0]
                self.params = params[1:]
            else:
                self.target = None
                self.params = params
        else:
            self.target = None
            self.params = []


class MessageEvent(StandardEvent):
    """ MessageEvent has all of the attributes as 
    :class:`ircutils.events.StandardEvent` with the added attribute ``message``
    which holds the message data.
    ::
       
           from ircutils import bot
           
           class PrinterBot(bot.SimpleBot):
               def on_message(self, event):
                   print "<{0}> {1}".format(event.source, event.message)
    
    """
    def __init__(self, prefix, command, params):
        StandardEvent.__init__(self, prefix, command, params)
        self.message = params[-1]


class CTCPEvent(StandardEvent):
    """ Represents a Client-To-Client Protocol (CTCP) event. """
    def __init__(self):
        self.source = None
        self.target = None
        self.command = None
        self.params = []



# ------------------------------------------------------------------------------
# > BEGIN EventListener AND HELPER CODE
# ------------------------------------------------------------------------------



class EventListener(object):
    """ This class is a simple event listener designed to be subclassed. Each
    event listener is in charge of activating its handlers. 
    """
    def __init__(self):
        self.handlers = []
    
    def add_handler(self, handler, priority=0):
        """ Add a handler to the event listener. It will be called when the 
        listener decides it's time. It will place it in order depending
        on the priority specified. The default is 0. 
        Event handlers take the form of::
            
            def my_handler(client, event):
                # Do stuff with the client and event here
                # Example: 
                client.send_message(event.target, "Hi!")
        
        If :class:`ircutils.bot.SimpleBot` is being used, you do not need to
        use this method as handlers are automatically added.
                
        """
        bisect.insort(self.handlers, (priority, handler))
    
    def remove_handler(self, handler):
        """ This removes all handlers that are equal to the ``handler`` which
        are bound to the event listener. This isn't too efficient since
        it is ``O(n^2)``.
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
            except StandardError, ex:
                traceback.print_exc(ex)
                self.handlers.remove((p, handler))
    
    def notify(self, client, event):
        """ This is to be overridden when subclassed. It gets called after each
        event generated by the system. If the event listener decides to, it
        should run its handlers from here.
        """
        raise NotImplementedError("notify() must be overridden.")





class _CustomListener(EventListener):
    
    def __init__(self, command, target, source):
        EventListener.__init__(self)
        self.command = command
        self.target = target
        self.source = source
    
    def notify(self, client, event):
        if self.command in (None, event.command) and \
           self.target  in (None, event.target)  and \
           self.source  in (None, event.source):
            self.activate_handlers(client, event)


def create_listener(command=None, target=None, source=None):
    """ Create a listener on-the-fly. This is the simplest way of creating event
    listeners, but also very limited. Examples::
    
        # Creates a listener that looks for events where the command is PRIVMSG
        msg_listener = events.create_listener(command="PRIVMSG")
        
        # Listens for events from the NickServ service
        ns_listener = events.create_lisener(source="NickServ")
        
        # Listens for events that are messages to a specific channel
        example = events.create_listener(command="PRIVMSG", target="#channel")
    """
    return _CustomListener(command, target, source)



# ------------------------------------------------------------------------------
# > BEGIN BUILT-IN EVENT LISTENERS
# ------------------------------------------------------------------------------


class ConnectListener(EventListener):
    def notify(self, client, event):
        if event.command == "CONN_CONNECT":
            self.activate_handlers(client, event)

class DisconnectListener(EventListener):
    def notify(self, client, event):
        if event.command == "CONN_DISCONNECT":
            self.activate_handlers(client, event)


connection = {
    "connect": ConnectListener,
    "disconnect": DisconnectListener
}



class AnyListener(EventListener):
    def notify(self, client, event):
        self.activate_handlers(client, event)

class WelcomeListener(EventListener):
    def notify(self, client, event):
        if event.command == "RPL_WELCOME":
            self.activate_handlers(client, event)

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



standard = {
    "any": AnyListener,
    "welcome": WelcomeListener,
    "ping": PingListener,
    "invite": InviteListener,
    "kick": KickListener,
    "join": JoinListener,
    "quit": QuitListener,
    "part": PartListener,
    "nick_change": NickChangeListener,
    "error": ErrorListener
    }



class MessageListener(EventListener):
    def notify(self, client, event):
        if event.command == "PRIVMSG":
            self.activate_handlers(client, event)

class PrivateMessageListener(MessageListener):
    def notify(self, client, event):
        if event.command == "PRIVMSG":
            if not protocol.is_channel(event.target):
                self.activate_handlers(client, event)

class ChannelMessageListener(MessageListener):
    def notify(self, client, event):
        if event.command == "PRIVMSG":
            if protocol.is_channel(event.target):
                self.activate_handlers(client, event)

class NoticeListener(MessageListener):
    def notify(self, client, event):
        if event.command == "NOTICE":
            self.activate_handlers(client, event)

class PrivateNoticeListener(NoticeListener):
    def notify(self, client, event):
        if event.command == "NOTICE":
            if not protocol.is_channel(event.target):
                self.activate_handlers(client, event)

class ChannelNoticeListener(NoticeListener):
    def notify(self, client, event):
        if event.command == "NOTICE":
            if protocol.is_channel(event.target):
                self.activate_handlers(client, event)



messages = {
    "message": MessageListener,
    "channel_message": ChannelMessageListener,
    "private_message": PrivateMessageListener,
    "notice": NoticeListener,
    "channel_notice": ChannelNoticeListener,
    "private_notice": PrivateNoticeListener
    }



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
        if event.command.startswith("CTCP_DCC"):
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
    "dcc": DCCListener
    }



class ReplyListener(EventListener):
    def notify(self, client, event):
        if event.command.startswith("RPL_"):
            self.activate_handlers(client, event)



class NameReplyListener(ReplyListener):
    
    class NameReplyEvent(Event):
        def __init__(self):
            self.channel = None
            self.name_list = []
    
    def __init__(self):
        ReplyListener.__init__(self)
        self._name_lists = collections.defaultdict(self.NameReplyEvent)
    
    def notify(self, client, event):
        if event.command == "RPL_NAMREPLY":
            # "( "=" / "*" / "@" ) <channel>
            # :[ "@" / "+" ] <nick> *( " " [ "@" / "+" ] <nick> )
            # 
            # - "@" is used for secret channels, "*" for private
            # channels, and "=" for others (public channels).
            channel = event.params[1].lower()
            names = event.params[2].strip().split(" ")
            # TODO: This line below is wrong. It doesn't use name symbols.
            names = map(protocol.strip_name_symbol, names)
            self._name_lists[channel].name_list.extend(names)
        elif event.command == "RPL_ENDOFNAMES":
            # <channel> :End of NAMES list
            channel_name = event.params[0]
            name_event = self._name_lists[channel_name]
            name_event.channel = channel_name
            self.activate_handlers(client, name_event)
            del self._name_lists[channel_name]



class ListReplyListener(ReplyListener):
    
    class ListReplyEvent(Event):
        def __init__(self, channel_list):
            self.channel_list = channel_list
    
    def __init__(self):
        ReplyListener.__init__(self)
        self.channel_list = []
    
    def notify(self, client, event):
        if event.command == "RPL_LIST":
            # <channel> <# visible> :<topic>
            channel_data = (event.params[0].lower(), event.params[1], event.params[2])
            self.channel_list.append(channel_data)
        elif event.command == "RPL_LISTEND":
            # :End of LIST
            list_event = self.ListReplyEvent(self.channel_list)
            self.activate_handlers(client, list_event)
            self.channel_list = []



class WhoisReplyListener(ReplyListener):
    """ http://tools.ietf.org/html/rfc1459#section-4.5.2 """
    
    class WhoisReplyEvent(Event):
        def __init__(self):
            self.nick = None
            self.user = None
            self.host = None
            self.real_name = None
            self.channels = []
            self.server = None
            self.is_operator = False
            self.idle_time = 0 # seconds
    
    def __init__(self):
        ReplyListener.__init__(self)
        self._whois_replies = collections.defaultdict(self.WhoisReplyEvent)
    
    def notify(self, client, event):
        if event.command == "RPL_WHOISUSER":
            # <nick> <user> <host> * :<real name>
            reply = self._whois_replies[event.params[1]]
            reply.nick = event.params[0] 
            reply.user = event.params[1] 
            reply.host = event.params[2] 
            reply.real_name = event.params[4]
        elif event.command == "RPL_WHOISCHANNELS":
            # <nick> :*( ( "@" / "+" ) <channel> " " )
            channels = event.params[1].strip().split()
            channels = map(protocol.strip_name_symbol, channels)
            self._whois_replies[event.params[0]].channels.extend(channels)
        elif event.command == "RPL_WHOISSERVER":
            # <nick> <server> :<server info> 
            self._whois_replies[event.params[0]].server = event.params[1]
        elif event.command == "RPL_WHOISIDLE":
            # <nick> <integer> :seconds idle
            self._whois_replies[event.params[0]].idle_time = event.params[1]
        elif event.command == "RPL_WHOISOPERATOR":
            # <nick> :is an IRC operator
            self._whois_replies[event.params[0]].is_operator = True
        elif event.command == "RPL_ENDOFWHOIS":
            # <nick> :End of WHOIS list
            self.activate_handlers(client, self._whois_replies[event.params[0]])
            del self._whois_replies[event.params[0]]



class WhoReplyListener(ReplyListener):
    """ http://tools.ietf.org/html/rfc1459#section-4.5.2 """
    
    class WhoReplyEvent(Event):
        def __init__(self):
            self.channel_name = None
            self.user_list = []
    
    def __init__(self):
        ReplyListener.__init__(self)
        self._who_replies = collections.defaultdict(self.WhoReplyEvent)
    
    def notify(self, client, event):
        if event.command == "RPL_WHOREPLY":
            channel = event.params[0].lower()
            user = protocol.User()
            user.user = event.params[1]
            user.host = event.params[2]
            user.server = event.params[3]
            user.nick = event.params[4]
            user.real_name = event.params[6].split()[1]
            self._who_replies[channel].user_list.append(user)
        elif event.command == "RPL_ENDOFWHO":
            channel = event.params[0].lower()
            self._who_replies[channel].channel_name = channel
            self.activate_handlers(client, self._who_replies[channel])




class ErrorReplyListener(ReplyListener):
    def notify(self, client, event):
        if event.command.startswith("ERR_"):
            self.activate_handlers(client, event)


replies = {
    "reply": ReplyListener,
    "name_reply": NameReplyListener,
    "list_reply": ListReplyListener,
    "whois_reply": WhoisReplyListener,
    "who_reply": WhoReplyListener,
    "error_reply": ErrorReplyListener
    }