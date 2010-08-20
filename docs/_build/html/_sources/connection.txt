ircutils.connection
===================
.. automodule:: ircutils.connection

.. note::
   The connection module is very low level and typically shouldn't be used
   directly. Most often you should be able to use the 
   :class:`ircutils.bot.SimpleBot` or the 
   :class:`ircutils.client.SimpleClient` instead.

The Connection class
--------------------
.. autoclass:: Connection
   :members: connect, execute, start, handle_line


Examples
--------
Here's an example where the `Connection` class is used to print messages from 
the server::

	from ircutils.connection import Connection
	
	class LowLevelMessageViewer(Connection):
	    
	    def handle_line(self, prefix, command, params):
	        if command == "PRIVMSG":
	            print prefix, params[0], params[1]
	
	
	if __name__ == "__main__":
	    conn = LowLevelMessageViewer()
	    conn.connect("irc.freenode.com")
	    conn.execute("USER", "example_bot", "+B", "*", trailing="example_bot")
	    conn.execute("NICK", "example_bot")
	    conn.execute("JOIN", "#botwar")
	    conn.start()

As you can see, it's pretty nitty-gritty doing it this way, but it works!