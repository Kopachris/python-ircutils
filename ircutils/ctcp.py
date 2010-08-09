""" 
    CTCP (client-to-client protocol) functions.
    
    Author:        Evan Fosmark <me@evanfosmark.com>
    Description:   Various utilities for managing the CTCP protocol. This module
                   is responsible for (1) parsing CTCP data and (2) making data
                   ready to be sent via CTCP.
"""
import re

X_DELIM = "\x01"
M_QUOTE = "\x10"
X_QUOTE = "\\"

commands = ["ACTION", "VERSION", "USERINFO", "CLIENTINFO", "ERRMSG", "PING", 
            "TIME", "FINGER"]


def tag(message):
    """ Wraps an X-DELIM (\x01) around a message to indicate that it needs to be
        CTCP tagged.
    """
    return X_DELIM + message + X_DELIM


def _parse_request(section):
    """ This function takes a CTCP-tagged section of a message and breaks it in
        to a two-part tuple in the form of (command, parameters) where `command`
        is a string and `parameters` is a tuple.
    """
    sections = section.split(" ")
    if len(sections) > 1:
        command, params = (sections[0], tuple(sections[1:]))
    else:
        command, params = (sections[0], tuple())
    return command, params


def find_tagged(message):
    """ Finds all CTCP-tagged data.
        Looks for data tagged with X-DELIM (\x01). It returns a list of tuples
        in the form of (command, parameters) where `parameters` is a tuple of
        parameters. This properly handles escaped X-DELIM characters by not
        counting them.
    """
    x_delim = r"(?<!\\)(?:\\\\)*\x01"
    ctcp_sections = re.findall("%s(.*?)%s" % (x_delim, x_delim), message, re.M)
    return map(_parse_request, ctcp_sections)


def strip_tagged(message):
    """ Removes all CTCP-tagged data.
        This is useful when one wishes to sanatize the message to the actual
        message itself.
    """
    return re.sub("\x01(.*?)\x01", "", message)



_ctcp_level_quote_chars = [
    ("\\",   "\\\\"),
    ("\x01", "\\a")
    ]


def quote(text):
    """ This is CTCP-level quoting. It's only purpose is to quote out \x01 
        characters so they can be represented INSIDE tagged CTCP data.
    """
    for (search, replace) in _ctcp_level_quote_chars:
        text = text.replace(search, replace)
    return text


def dequote(text):
    """ Performs the opposite of `quote()` as it will essentially strip the 
        quote character.
    """
    for (replace, search) in reversed(_ctcp_level_quote_chars):
        text = text.replace(search, replace)
    return text



_low_level_quote_chars = [
    ("\x00",  "\x100"),
    ("\n",    "\x10n"),
    ("\r",    "\x10r"),
    ("\x10",  "\x10\x10")
    ]


def low_level_quote(text):
    """ Performs a low-level quoting in order to escape characters that could
        otherwise not be represented in the typical IRC protocol.
    """
    # TODO: Strip cases where M_QUOTE is on its own
    for (search, replace) in _low_level_quote_chars:
        text = text.replace(search, replace)
    return text


def low_level_dequote(text):
    """ Performs the complete opposite of `low_level_quote` as it converts the
        quoted character back to their original forms.
    """
    for (replace, search) in reversed(_low_level_quote_chars):
        text = text.replace(search, replace)
    return text

