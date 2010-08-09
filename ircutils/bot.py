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



class IRCBot(client.SimpleClient):
    """ A simple IRC bot to subclass.
        When subclassing, make methods in the form of ``on_eventname`` and they
        will automatically be bound to that event listener.
    """
    def __init__(self, nick):
        client.SimpleClient.__init__(self, nick)
        for listener_name in self.events:
            name = "on_%s" % listener_name
            if hasattr(self, name):
                handler = getattr(self, name).__func__
                self.events[listener_name].add_handler(handler)


class _BotCommand(object):
    
    def __init__(self, name, callback, desc="", case_sensitive=False):
        self.name = name
        self.callback = callback
        self.case_sensitive = case_sensitive
        self.desc = desc


class _BotCommandEvent(events.Event):
    
    def __init__(self):
        events.Event.__init__(self)
        self.origin = None
        self.command = None
        self.params = []


class _BotCommandListener(events.EventListener):
    
    _regex = """
        (?i)^
        ((h(e|a)y|yo|(h|y|j)?ello|hi|l(o*|aw)l|so|(u)+(h)*(m)*)\s+|)+
        %(nick)s[;:,\.]?
        \s*
        (?P<command>.+)
        """
    
    def notify(self, client, event):
        if event.command != "PRIVMSG":
            return False
        if event.params[0] != client.nickname:
            regexp = self._regex % {"nick": re.escape(client.nickname)}
            match = re.search(regexp, event.trailing, re.VERBOSE)
            if not match:
                return False
            command_data = match.group("command").split()
        elif event.trailing.strip() != "":
            command_data = event.trailing.split()
        else:
            return False
        command_event = _BotCommandEvent()
        command_event.origin = event.origin
        command_event.target = event.params[0]
        if " " in command_data:
            command_event.command = command_data[0]
            command_event.params = command_data[1:]
        else:
            command_event.command = command_data[0]
        self.activate_handlers(client, command_event)




class AdvancedIRCBot(IRCBot):
    
    def __init__(self, nick, description=""):
        IRCBot.__init__(self, nick)
        self.description = description
        self.commands = {}
        self.defaults = []
        self.events["bot_command"] = _BotCommandListener()
        self.events["bot_command"].add_handler(self._dispatch_command)

    def bind(self, cmd_name, callback, desc="", case_sensitive=False):
        command = _BotCommand(cmd_name, callback, desc, case_sensitive)
        self.commands[cmd_name] = command
    
    def bind_default(self, callback):
        self.defaults.append(callback)
    
    def _dispatch_command(self, client, command_event):
        match_occured = False
        for command_name, bot_command in self.commands.items():
            if command_event.command == command_name:
                match_occured = True
                bot_command.callback(client, command_event)
        if not match_occured:
            for handler in self.defaults:
                bot_command.callback(client, command_event)




def help_handler(bot, event):
    """ Help message output script.
        Use this as a bot command callback as a means to easily generate help
        text for the registered commands.
        Note: This does not take in to account permissions.
    """
    command_desc = {}
    no_desc = []
    for name, bot_command in bot.commands.items():
        if bot_command.desc == "":
            no_desc.append(bot_command.name.upper())
        else:
            command_desc[bot_command.name.upper()] = bot_command.desc
    help_msg = [bold("***** %s Help *****" % bot.nickname)]
    help_msg.append(bot.description)
    #help_msg.append("For information about a specific command, type:")
    #help_msg.append(bold("/msg %s HELP <command>" % bot.nickname))
    help_msg.append(" ")
    help_msg.append("The following commands are available:")
    for name, desc in command_desc.items():
        help_msg.append("%-15s %s" % (bold(name), desc))
    help_msg.append(" ")
    help_msg.append(bold("Other commands: ") + ", ".join(no_desc))
    help_msg.append(bold("***** End of Help *****"))
    for message in help_msg:
        bot.send_notice(event.origin, message)
        time.sleep(0.3)



if __name__ == "__main__":
    x = lambda:True
    
    testbot = AdvancedIRCBot("KingCog")
    testbot.connect("irc.freenode.com")
    
    testbot.bind("HELP", help_handler, desc="Shows this")
    testbot.bind("TEST", x, desc="Test the bot for workingness.")
    testbot.bind("AUTH", x, desc="Perform authentication.")
    testbot.bind("FOO",  x, desc="Run the fubar.")
    testbot.bind("BAR",  x)
    testbot.bind("SPAM", x)
    testbot.bind("EGGS", x)
    
    
    def on_join(client, event):
        client.send_message(event.params[0], "hello!\nhow are you?")
    
    
    def on_welcome(client, event):
        client.join_channel("#ircutils")
    
    testbot.events["join"].add_handler(on_join)
    testbot.events["welcome"].add_handler(on_welcome)
    testbot.start()