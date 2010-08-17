ircutils.bot
=============
.. automodule:: ircutils.bot


SimpleBot
-------------
.. autoclass:: SimpleBot
   :members:


Example
--------

A quick "Hello, world!" bot::
	
	from ircutils import bot
	
	class ExampleBot(bot.SimpleBot):
	    """ A simple "Hello, world!" bot. It connects to the server, joins 
	        #ircutils once it receives the welcome message, and then when it 
	        joins a channel it will send "Hello, world!"
	    """
	    def on_welcome(self, event):
	        self.join("#ircutils")
	    
	    def on_join(self, event):
	        if event.source == self.nickname: 
	            self.send_message(event.target, "Hello, world!")
	
	if __name__ == "__main__":
	    example = ExampleBot("example_bot")
	    example.connect("irc.freenode.com")
	    example.start()
	  
