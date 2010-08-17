ircutils.ident
==============
.. automodule:: ircutils.ident


Servers
-------
.. note:: 
   The standard ident port is 113; however, since on many operating systems 
   any port below 1024 is protected, you may either have to  have root access.
   Otherwise, set up a port forward that goes from 113 to something higher, 
   and serve on that.

.. autoclass:: FakeIdentServer
   :members: start

.. autoclass:: IdentServer
   :members: start


Client
------
.. autoclass:: IdentClient
   :members:


Example
-------
Running an ident server typically isn't necessary, but some servers require
it to connect. It does, however, make startup time much less since the client
doesn't have to wait at the "Checking for ident..." phase::

	from ircutils import bot, ident, start_all
	
	class ExampleBot(bot.SimpleBot):
	    
	    def on_welcome(self, event):
	        self.join("#ircutils")
	    
	    def on__channel_message(self, event):
	        print "|<--|", event.message

	if __name__ == "__main__":
		
		# Set up the bot
		example = ExampleBot("example_bot")
		
		# Set up the ident server
		# We use 1113 here because 113 is protected by the operating system, 
		# so we have to forward port 113 on the router to 1113 locally.
		identd = ident.FakeIdentServer(port=1113)
		
		# Since we are running more than one server at the same time, we want to 
		# take advantage of the asynchronous nature of IRCUtils, so we start 
		# them together.
		start_all()