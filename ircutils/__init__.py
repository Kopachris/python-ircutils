
__author__ = "Evan Fosmark"
__all__ = ["bot", "client", "connection", "ctcp", "events", "format", "ident",
           "protocol", "responses"]


def start_all():
    """ Begins all waiting clients. """
    import asyncore
    asyncore.loop()