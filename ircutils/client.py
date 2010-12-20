""" This module provides a direct client interface for managing an IRC 
connection. If you are trying to build a bot, :class:`ircutils.bot.SimpleBot` 
inherits from :class:`SimpleClient` so it has the methods listed below.

"""
import collections

import connection
import ctcp
import events
import format
import protocol


class SimpleClient(object):
    """ SimpleClient is designed to provide a high level of abstraction
    of the IRC protocol. It's methods are structured in a way that allows
    you to often bypass the need to send raw IRC commands. By default, 
    ``auto_handle`` is set to ``True`` and allows the client to handle the 
    following:
    
      * Client nickname changes
      * Client channel tracking
      * CTCP version requests
    
    """
    software = "http://dev.guardedcode.com/projects/ircutils/"
    version = (0,1,3)
    custom_listeners = {}
    
    def __init__(self, nick, mode="+B", auto_handle=True):
        self.nickname = nick
        self.user = nick
        self.real_name = self.software
        self.filter_formatting = True
        self.channels = collections.defaultdict(protocol.Channel)
        self.events = events.EventDispatcher()
        self._prev_nickname = None
        self._mode = mode
        self._register_default_listeners()
        if auto_handle:
            self._add_built_in_handlers()

    
    def __getitem__(self, name):
        return self.events[name]
    
    def __setitem__(self, name, value):
        self.register_listener(name, value)
    
    
    def _register_default_listeners(self):
        """ Registers the default listeners to the names listed in events. """
        
        # Connection events
        for name in events.connection:
            self.events.register_listener(name, events.connection[name]())
        
        # Standard events
        for name in events.standard:
            self.events.register_listener(name, events.standard[name]())
        
        # Message events
        for name in events.messages:
            self.events.register_listener(name, events.messages[name]())
        
        # CTCP events
        for name in events.ctcp:
            self.events.register_listener(name, events.ctcp[name]())
        
        # RPL_ events
        for name in events.replies:
            self.events.register_listener(name, events.replies[name]())
        
        # Custom listeners
        for name in self.custom_listeners:
            self.events.register_listener(name, self.custom_listeners[name])
    
    
    def _add_built_in_handlers(self):
        """ Adds basic client handlers.
        These handlers are bound to events that affect the data the the
        client handles. It is required to have these in order to keep
        track of things like client nick changes, joined channels, 
        and channel user lists.
        """
        self.events["any"].add_handler(_update_client_info)
        self.events["name_reply"].add_handler(_set_channel_names)
        self.events["ctcp_version"].add_handler(_reply_to_ctcp_version)
        self.events["part"].add_handler(_remove_channel_user_on_part)
        self.events["quit"].add_handler(_remove_channel_user_on_quit)
        self.events["join"].add_handler(_add_channel_user)
    
    
    def _dispatch_event(self, prefix, command, params):
        """ Given the parameters, dispatch an event.
        After first building an event, this method sends the event(s) to the
        primary event dispatcher.
        This replaces :func:`connection.Connection.handle_line`
        """
        pending_events = []
        # TODO: Event parsing doesn't belong here.
        
        if command in ["PRIVMSG", "NOTICE"]:
            event = events.MessageEvent(prefix, command, params)
            message_data = event.params[-1]
            message_data = ctcp.low_level_dequote(message_data)
            message_data, ctcp_requests = ctcp.extract(event.params[-1])
            if self.filter_formatting:
                message_data = format.filter(message_data)
            if message_data.strip() != "":
                event.message = message_data
                pending_events.append(event)
            for command, params in ctcp_requests:
                ctcp_event = events.CTCPEvent()
                ctcp_event.command = "CTCP_%s" % command
                ctcp_event.params = params
                ctcp_event.source = event.source
                ctcp_event.target = event.target
                pending_events.append(ctcp_event)
        else:
            pending_events.append(events.StandardEvent(prefix, command, params))
        
        for event in pending_events:
            self.events.dispatch(self, event)
    
    
    def connect(self, host, port=None, channel=None, use_ssl=False, 
                password=None):
        """ Connect to an IRC server. """
        self.conn = connection.Connection()
        self.conn.handle_line = self._dispatch_event
        self.conn.connect(host, port, use_ssl, password)
        self.conn.execute("USER", self.user, self._mode, "*", 
                                  trailing=self.real_name)
        self.conn.execute("NICK", self.nickname)
        self.conn.handle_connect = self._handle_connect
        self.conn.handle_close = self._handle_disconnect
        
        if channel is not None:
            # Builds a handler on-the-fly for joining init channels
            
            if isinstance(channel, basestring):
                channels = [channel]
            else:
                channels = channel
            
            def _auto_joiner(client, event):
                for channel in channels:
                    client.join_channel(channel)
            
            self.events["welcome"].add_handler(_auto_joiner)
    
    
    def is_connected(self):
        return self.conn.connected
    
    def _handle_connect(self):
        connection.Connection.handle_connect(self.conn)
        event = events.ConnectionEvent("CONN_CONNECT")
        self.events.dispatch(self, event)
    
    def _handle_disconnect(self):
        connection.Connection.handle_close(self.conn)
        event = events.ConnectionEvent("CONN_DISCONNECT")
        self.events.dispatch(self, event)
    
    
    def register_listener(self, event_name, listener):
        """ Registers an event listener for a given event name.
        In essence, this binds the event name to the listener and simply 
        provides an easier way to reference the listener.
        ::
        
            client.register_listener("event_name", MyListener())
        """
        self.events.register_listener(event_name, listener)
    
    
    def identify(self, ns_password):
        """ Identify yourself with the NickServ service on IRC.
        This assumes that NickServ is present on the server.
        
        """
        self.send_message("NickServ", "IDENTIFY {0}".format(ns_password))
    
    
    def join_channel(self, channel, key=None):
        """ Join the specified channel. Optionally, provide a key to the channel
        if it requires one.
        ::
        
            client.join_channel("#channel_name")
            client.join_channel("#channel_name", "channelkeyhere")
        """
        if channel == "0":
            self.channels = []
            self.conn.execute("JOIN", "0")
        else:
            if key is not None:
                params = [channel, key]
            else:
                params = [channel]
            self.conn.execute("JOIN", *params)
    
    
    def part_channel(self, channel, message=None):
        """ Leave the specified channel.
        You may provide a message that shows up during departure.
            
        """
        self.conn.execute("PART", channel, trailing=message)
    
    
    def send_message(self, target, message, to_service=False):
        """ Sends a message to the specified target.
        If it is a service, it uses SQUERY instead.
        
        """
        message = ctcp.low_level_quote(message)
        if to_service:
            self.conn.execute("SQUERY", target, message)
        else:
            self.conn.execute("PRIVMSG", target, trailing=message)
    
    
    def send_notice(self, target, message):
        """ Sends a NOTICE to the specified target. 
        
        """
        message = ctcp.low_level_quote(message)
        self.conn.execute("NOTICE", target, trailing=message)
    
    
    def send_ctcp(self, target, command, params=None):
        """ Sends a CTCP (Client-to-Client-Protocol) message to the target. 
        
        """
        if params is not None:
            params.insert(0, command)
            self.send_message(target, ctcp.tag(" ".join(params)))
        else:
            self.send_message(target, ctcp.tag(command))
    
    
    def send_ctcp_reply(self, target, command, params=None):
        """ Sends a CTCP reply message to the target. 
        This differs from send_ctcp() because it uses NOTICE instead, as
        specified by the CTCP documentation.
        
        """
        if params is not None:
            params.insert(0, command)
            self.send_notice(target, ctcp.tag(" ".join(params)))
        else:
            self.send_notice(target, ctcp.tag(command))
    
    
    def send_action(self, target, action_message):
        """ Perform an "action". This is the same as when a person uses the
        ``/me is jumping up and down!`` command in their IRC client.

        """
        self.send_ctcp(target, "ACTION", [action_message])
    
    
    def set_nickname(self, nickname):
        """ Attempts to set the nickname for the client. """
        self._prev_nickname = self.nickname
        self.conn.execute("NICK", nickname)
    
    
    def disconnect(self, message=None):
        """ Disconnects from the IRC server.
        If `message` is set, it is provided as a departing message.
        Example::
        
            client.disconnect("Goodbye cruel world!")
        """
        self.conn.execute("QUIT", trailing=message)
        self.channels = []
        self.conn.close_when_done()

    
    def start(self):
        """ Begin the client. 
        If you wish to run multiple clients at the same time, be sure to
        use ``ircutils.start_all()`` instead.
        
        """
        self.conn.start()
    
    
    def execute(self, command, *args, **kwargs):
        """ Execute an IRC command on the server.  
        Example::
            
            self.execute("PRIVMSG", channel, trailing="Hello, world!")
            
        """
        self.conn.execute(command, *args, **kwargs)
    
    
    # Some less verbose aliases
    join = join_channel
    part = part_channel
    notice = send_notice
    action = send_action
    quit = disconnect



# TODO: UPDATE EVERYTHING HERE.

def _reply_to_ctcp_version(client, event):
    version_info = "IRCUtils:%s:Python" % ".".join(map(str, client.version))
    client.send_ctcp_reply(event.source, "VERSION", [version_info])


def _update_client_info(client, event):
    command = event.command
    params = event.params
    if command == "RPL_WELCOME":
        if client.nickname != event.target:
            client.nickname = event.target
    if command == "ERR_ERRONEUSNICKNAME":
        client.set_nickname(protocol.filter_nick(client.nickname))
    elif command == "ERR_NICKNAMEINUSE":
        client.set_nickname(client.nickname + "_")
    elif command == "ERR_UNAVAILRESOURCE":
        if not protocol.is_channel(event.params[0]):
            client.nickname = client._prev_nickname
    elif command == "NICK" and event.source == client.nickname:
        client.nickname = event.target
    
    if command in ["ERR_INVITEONLYCHAN", "ERR_CHANNELISFULL",  "ERR_BANNEDFROMCHAN", 
                   "ERR_BADCHANNELKEY", "ERR_TOOMANYCHANNELS", "ERR_NOSUCHCHANNEL"
                   "ERR_BADCHANMASK"]:
        channel_name = params[0].lower()
        if channel_name in client.channels:
            del client.channels[channel_name]
    elif command == "ERR_UNAVAILRESOURCE":
        channel_name = params[0].lower()
        if protocol.is_channel(channel_name) and channel_name in client.channels:
            del client.channels[channel_name]


def _set_channel_names(client, name_event):
    channel_name = name_event.channel.lower()
    client.channels[channel_name].name = channel_name
    client.channels[channel_name].user_list = name_event.name_list


def _remove_channel_user_on_part(client, event):
    channel = event.target.lower()
    if event.source == client.nickname:
        del client.channels[channel]
    elif event.source in client.channels[channel].user_list:
        client.channels[channel].user_list.remove(event.source)


def _remove_channel_user_on_quit(client, event):
    # TODO: This solution is slow. There might be a better one.
    for channel in client.channels:
        if event.source in client.channels[channel].user_list:
            client.channels[channel].user_list.remove(event.source)


def _add_channel_user(client, event):
    channel = event.target.lower()
    client.channels[channel].user_list.append(event.source)