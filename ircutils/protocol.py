"""Provide various IRC protocol utility methods and classes. Provide a parser
and a generator."""

import string
from collections import UserString
from datetime import datetime


irc_uppercase = string.ascii_uppercase + "[]\~"
irc_lowercase = string.ascii_lowercase + "{}|^"
upper_to_lower = str.maketrans(irc_uppercase, irc_lowercase)
lower_to_upper = str.maketrans(irc_lowercase, irc_uppercase)


class IRCstr(UserString):
    """Implement str, overriding case-changing methods to only handle ASCII
    cases plus "{}|^" and "[]\~" as defined by RFC 2812.

    Hashing and equality testing is case insensitive! That is, __hash__ will
    return the hash of the lowercase version of the string, and __eq__ will
    convert both operands to lowercase before testing equality.
    """

    def casefold(self):
        return self.lower()

    def lower(self):
        return self.data.translate(upper_to_lower)

    def upper(self):
        return self.data.translate(lower_to_upper)

    def islower(self):
        return self.data == self.lower()

    def isupper(self):
        return self.data == self.upper()

    def __hash__(self):
        return hash(self.lower())

    def __eq__(self, other):
        if isinstance(other, IRCstr):
            return self.lower() == other.lower()
        elif isinstance(other, str):
            # Use our custom lowercasing for IRC on other
            return self.lower() == other.translate(upper_to_lower)
        else:
            return False


class IRCUser:
    """Represents one IRC user."""

    def __init__(self, nick, user, host):
        self.nick = IRCstr(nick)
        self.user = user
        self.host = host
        self.channels = []

    def join(self, channel):
        """Add this user to the channel's user list and add the channel to this
        user's list of joined channels.
        """

        if channel not in self.channels:
            channel.users.add(self.nick)
            self.channels.append(channel)

    def part(self, channel):
        """Remove this user from the channel's user list and remove the channel
        from this user's list of joined channels.
        """

        if channel in self.channels:
            channel.users.remove(self.nick)
            self.channels.remove(channel)

    def quit(self):
        """Remove this user from all channels and reinitialize the user's list
        of joined channels.
        """

        for c in self.channels:
            c.users.remove(self.nick)
        self.channels = []

    def change_nick(self, nick):
        """Update this user's nick in all joined channels."""

        old_nick = self.nick
        self.nick = IRCstr(nick)

        for c in self.channels:
            c.users.remove(old_nick)
            c.users.add(self.nick)

    def __str__(self):
        return "{}!{}@{}".format(self.nick, self.user, self.host)

    def __repr__(self):
        temp = "<IRCUser {}!{}@{} in channels {}>"
        return temp.format(self.nick, self.user, self.host, self.channels)


class IRCChannel(object):
    """Represent one IRC channel."""

    def __init__(self, name, users, log_size=100):
        self.name = IRCstr(name)
        self.users = users
        self.message_log = []
        self._log_size = log_size

    def log_message(self, user, message):
        """Log a channel message.

        This log acts as a sort of cache so that recent activity can be searched
        by a client without opening a file or querying a database.
        """

        if isinstance(user, IRCUser):
            user = user.nick
        elif not isinstance(user, IRCstr):
            user = IRCstr(user)

        time = datetime.utcnow()

        self.message_log.append((time, user, message))

        while len(self.message_log) > self._log_size:
            del self.message_log[0]

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        temp = "<IRCChannel {} with {} users>"
        return temp.format(self.name, len(self.users))