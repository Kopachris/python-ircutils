ircutils.format
=================

.. note::
   If the channel you're on has ``+c`` in the mode active, no formatting will be
   available as the server automatically strips all of the tags.

.. automodule:: ircutils.format
   :members:

Examples
--------
Here are a few examples that should help get you started with learning how to 
format text.

**Bold demonstration**
    For this, we'll be using :func:`ircutils.format.bold`::

	from ircutils import bot, format
	
	class ExampleBot(bot.SimpleBot):
	    
	    def on_welcome(self, event):
	        self.join("#ircutils")
	    
	    def on_join(self, event):
	        if event.source == self.nickname: 
	            message = format.bold("Hello bold world!")
	            self.send_message(event.target, message)


**Let's add some color**
    For this, we'll be using :func:`ircutils.format.color`::

	from ircutils import bot, format
	
	class ExampleBot(bot.SimpleBot):
	    
	    def on_welcome(self, event):
	        self.join("#ircutils")
	    
	    def on_join(self, event):
	        if event.source == self.nickname: 
	            message = format.bold("Hello bold and green world!")
	            message = format.color(message, format.GREEN)
	            self.send_message(event.target, message)


**Remove all formatting**
    All of this formatting is great and all, but let's sanatize the messages 
    coming in by removing the formatting using :func:`ircutils.format.filter`::

	from ircutils import bot, format
	
	class ExampleBot(bot.SimpleBot):
	    
	    def on_welcome(self, event):
	        self.join("#ircutils")
	    
	    def on_message(self, event):
	        message = format.filter(event.message)
	        print "Message recieved:", message

**Remove just color tags**
    Let's say that for some reason we want to keep everything but the color in a
    message. Then, all we have to do is apply a more restrictive filter to it::

	from ircutils import bot, format
	
	class ExampleBot(bot.SimpleBot):
	    
	    def on_welcome(self, event):
	        self.join("#ircutils")
	    
	    def on_message(self, event):
	        message = format.filter(event.message, format.FILTER_COLOR)
	        print "Message recieved:", message
