""" This module has various utilities for managing the CTCP protocol. It is
is responsible for parsing CTCP data and making data ready to be sent 
via CTCP.

"""

X_DELIM = "\x01"
M_QUOTE = "\x10"
X_QUOTE = "\\"

commands = ["ACTION", "VERSION", "USERINFO", "CLIENTINFO", "ERRMSG", "PING", 
            "TIME", "FINGER"]

_ctcp_level_quote_map = [
    ("\\",   "\\\\"),
    ("\x01", "\\a")
    ]

_low_level_quote_map = [
    ("\x10",  "\x10\x10"),
    ("\x00",  "\x100"),
    ("\n",    "\x10n"),
    ("\r",    "\x10r")
    ]


def tag(message):
    """ Wraps an X-DELIM (``\\x01``) around a message to indicate that it needs 
    to be CTCP tagged.
    
    """
    return X_DELIM + message + X_DELIM


def low_level_quote(text):
    """ Performs a low-level quoting in order to escape characters that could
    otherwise not be represented in the typical IRC protocol.
     
    """
    # TODO: Strip cases where M_QUOTE is on its own
    for (search, replace) in _low_level_quote_map:
        text = text.replace(search, replace)
    return text


def low_level_dequote(text):
    """ Performs the complete opposite of ``low_level_quote`` as it converts the
    quoted character back to their original forms.
    
    """
    # TODO: Strip cases where M_QUOTE is on its own
    for (replace, search) in reversed(_low_level_quote_map):
        text = text.replace(search, replace)
    return text


def quote(text):
    """ This is CTCP-level quoting. It's only purpose is to quote out ``\\x01`` 
    characters so they can be represented INSIDE tagged CTCP data.
    
    """
    for (search, replace) in _ctcp_level_quote_map:
        text = text.replace(search, replace)
    return text


def dequote(text):
    """ Performs the opposite of ``quote()`` as it will essentially strip the 
    quote character.
    
    """
    for (replace, search) in reversed(_ctcp_level_quote_map):
        text = text.replace(search, replace)
    return text


def extract(message):
    """ Splits a message between the actual message and any CTCP requests.
    It returns a 2-part tuple of ``(message, ctcp_requests)`` where 
    ``ctcp_requests`` is a list of requests.
    
    """
    stripped_message = []
    ctcp_requests = []
    in_tag = False
    index = 0
    while index < len(message):
        if in_tag:
            ctcp_request = []
            while index < len(message) and message[index] != X_DELIM:
                ctcp_request.append(message[index])
                index += 1
            ctcp_requests.append(_parse_request("".join(ctcp_request)))
            in_tag = False
        else:
            while index < len(message) and message[index] != X_DELIM:
                stripped_message.append(message[index])
                index += 1
            in_tag = True
        index += 1
    return "".join(stripped_message), ctcp_requests


def _parse_request(section):
    """ This function takes a CTCP-tagged section of a message and breaks it in
    to a two-part tuple in the form of ``(command, parameters)`` where 
    ``command`` is a string and ``parameters`` is a tuple.
    
    """
    sections = section.split(" ")
    if len(sections) > 1:
        command, params = (sections[0], tuple(sections[1:]))
    else:
        command, params = (sections[0], tuple())
    return command, params