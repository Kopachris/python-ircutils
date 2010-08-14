"""
    Asynchronous IRC connection management.
    
    Author:       Evan Fosmark <me@evanfosmark.com>
    Description:  Tasked with managing inputs and outputs of an IRC 
                  client connection.
"""
import collections

import connection
import ctcp
import events
import protocol


class SimpleClient(object):
    
    software = "ircutils <http://dev.guardedcode.com/projects/ircutils>"
    version = (0,4,3)
    
    def __init__(self, nick, ident=None, mode="+B", real_name=software):
        self.conn = connection.Connection()
        self.conn.handle_line = self._dispatch_event
        self.prev_nickname = None
        self.nickname = nick
        self.ident = (ident, nick)[ident is None]
        self.mode = mode
        self.real_name = real_name
        self.channels = collections.defaultdict(protocol.Channel)
        self.events = events.EventDispatcher()
        self._register_default_listeners()
        self._add_standard_handlers()

    
    def _register_default_listeners(self):
        """ Registers the default listeners to the names listed in events.
            Default listeners include:
                Standard events -- events.standard
                CTCP events -- events.ctcp
                RPL_ events -- events.replies
        """
        
        # Standard events
        for name, listener in events.standard:
            self.events.register_listener(name, listener())
        
        # CTCP events
        for name, listener in events.ctcp:
            self.events.register_listener(name, listener())
        
        # RPL_ events
        for name, listener in events.replies:
            self.events.register_listener(name, listener())
    
    
    def _add_standard_handlers(self):
        """ Adds basic client handlers.
            These handlers are bound to events that affect the data the the
            client handles. It is required to have these in order to keep
            track of things like client nick changes, joined channels, 
            and channel user lists.
        """
        self.events["any"].add_handler(_update_client_info)
        self.events["name_reply"].add_handler(_set_channel_names)
        self.events["part"].add_handler(_remove_channel_user)
        self.events["quit"].add_handler(_remove_channel_user)
        self.events["join"].add_handler(_add_channel_user)
    
    
    def _dispatch_event(self, prefix, command, params):
        """ Given the parameters, dispatch an event.
            After first building an event, this method sends the event(s) to the
            primary event dispatcher.
            This replaces connection.Connection.handle_line
        """
        event = events.LineEvent(prefix, command, params)
        if event.command in ["PRIVMSG", "NOTICE"]:
            event.trailing = ctcp.low_level_dequote(event.trailing)
            event.trailing, ctcp_requests = ctcp.extract(event.trailing)
            if event.trailing.strip() != "":
                self.events.dispatch(self, event)
            for request in ctcp_requests:
                if " " not in request:
                    command = request
                    params = []
                else:
                    request_parts = request.split()
                    command = "CTCP_%s" % request_parts[0]
                    params = request_parts[1:]
                ctcp_event = events.CTCPEvent(command, params)
                self.events.dispatch(self, ctcp_event)
        else:
            self.events.dispatch(self, event)
    
    
    def connect(self, hostname, port=6667, use_ssl=False, password=None):
        """ Connect to an IRC server.
        
        Arguments:
          hostname -- The host which you wish to connect
          port     -- The port to use
          use_ssl  -- True or false depending on whether it is an SSL connection
          password -- The server password, if one exists.
        """
        self.conn.connect(hostname, port, use_ssl, password)
        self.conn.execute("USER", self.ident, self.mode, "*", 
                                  trailing=self.real_name)
        self.conn.execute("NICK", self.nickname)
    
    
    def register_listener(self, event_name, listener):
        """ Registers an event listener for a given event name.
            In essence, this binds the event name to the listener and simply 
            provides an easier way to reference the listener.
        """
        self.dispatcher.register_listener(event_name, listener)
    
    
    def identify(self, ns_password):
        """ Identify yourself with the NickServ service on IRC.
            This assumes that NickServ is present on the server.
        """
        self.send_message("NickServ", "IDENTIFY %s" % ns_password)
    
    
    def join_channel(self, channel, key=None):
        """ Join the specified channel.
            Optionally, provide a key to the channel if it requires one.
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
        message = ctcp.low_level_quote(message)
        if to_service:
            self.conn.execute("SQUERY", target, message)
        else:
            self.conn.execute("PRIVMSG", target, trailing=message)
    
    def send_notice(self, target, message):
        message = ctcp.low_level_quote(message)
        self.conn.execute("NOTICE", target, trailing=message)
    
    def send_ctcp(self, target, command, params=None):
        if params is not None:
            params.insert(0, command)
            self.send_message(target, ctcp.tag(" ".join(params)))
        else:
            self.send_message(target, ctcp.tag(command))
    
    def send_ctcp_reply(self, target, command, params=None):
        if params is not None:
            params.insert(0, command)
            self.send_notice(target, ctcp.mark(" ".join(params)))
        else:
            self.send_notice(target, ctcp.mark(command))
    
    def set_nickname(self, nickname):
        self.prev_nickname = self.nickname
        self.conn.execute("NICK", nickname)
    
    def quit(self, message=None):
        self.conn.execute("QUIT", trailing=message)
        self.channels = []
    
    def set_topic(self, topic):
        self.conn.execute("TOPIC", trailing=topic)
    
    def set_mode(self, target, mode_string):
        self.conn.execute("MODE", target, mode_string)
    
    def send_invite(self, target, channel):
        self.conn.execute("INVITE", target, channel)
    
    def kick_user(self, channel, user, comment=None):
        self.conn.execute("KICK", channel, user, trailing=comment)
    
    def start(self):
        self.conn.start()
    
    # Some less verbose aliases
    join = join_channel
    part = part_channel
    privmsg = send_message
    notice = send_notice
    nick = set_nickname
    invite = send_invite
    kick = kick_user



def _update_client_info(client, event):
    command = event.command
    params = event.params
    
    if command == "ERR_ERRONEUSNICKNAME":
        client.set_nickname(protocol.filter_nick(client.nickname))
    elif command == "ERR_NICKNAMEINUSE":
        client.set_nickname(client.nickname + "_")
    elif command == "ERR_UNAVAILRESOURCE":
        if not protocol.is_channel(event.params[0]):
            client.nickname = client.prev_nickname
    elif command == "NICK" and event.origin == client.nickname:
        client.nickname = event.trailing
    
    if command in ["ERR_INVITEONLYCHAN", "ERR_CHANNELISFULL", 
                   "ERR_BANNEDFROMCHAN", "ERR_BADCHANNELKEY", 
                   "ERR_TOOMANYCHANNELS"]:
        if params[0] in client.channels:
            del client.channels[params[0]]
    elif command == "ERR_NOSUCHCHANNEL" and params[0] in client.channels:
        del client.channels[params[0]]
    elif command == "ERR_BADCHANMASK" and params[0] in client.channels:
        del client.channels[params[0]]
    elif command == "ERR_UNAVAILRESOURCE":
        if protocol.is_channel(params[0]) and params[0] in client.channels:
            del client.channels[params[0]]


def _set_channel_names(client, name_event):
    print name_event.channel, name_event.name_list
    channel_name = name_event.channel
    client.channels[channel_name].user_list = name_event.name_list

def _remove_channel_user(client, event):
    channel = event.params[0]
    if event.origin == client.nickname:
        del client.channels[channel]
    elif event.origin in client.channels[channel].user_list:
        client.channels[channel].user_list.remove(event.origin)

def _add_channel_user(client, event):
    channel = event.params[0]
    client.channels[channel].user_list.append(event.origin)