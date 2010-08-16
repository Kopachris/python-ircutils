
__author__ = "Evan Fosmark"
__all__ = ["bot", "client", "connection", "ctcp", "events", "format", "ident",
           "responses", "util"]


def start_all():
    """ Begins all waiting clients. """
    import asyncore
    asyncore.start()