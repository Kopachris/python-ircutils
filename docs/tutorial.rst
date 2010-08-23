Tutorial
========
This tutorial is designed to give you a small taste of what IRCUtils has to 
offer you in terms of IRC solutions.


Getting warmed up
-----------------
It'll be an IRC bot that that simply responds to any channel message with that 
same message. We'll call it `EchoBot`. First, since we're using IRCUtils to 
make a bot, we'll need to import the proper module::

    from ircutils import bot

We'll use :class:`ircutils.bot.SimpleBot` to build upon. To do this, create a
new class by extending it::

    from ircutils import bot

    class EchoBot(bot.SimpleBot):
        # The bot is currently empty
        # We'll add event handlers next!
        pass

Right now, we actually have a working IRC bot; however, it isn't able to respond
to any events since we haven't added any event handlers. When using
``SimpleBot``, event handlers are created by adding methods in the form of
``on_event_name(self, event)`` where the ``event_name`` is whatever event you
wish to handle.

Let's tell it to connect to ``#ircutils`` once it receives the 
IRC welcome message by using the ``on_welcome`` event handler::

    from ircutils import bot

    class EchoBot(bot.SimpleBot):
        
        def on_welcome(self, event):
            self.join("#ircutils")

So here we have our first true introduction to events and event handlers. 
Before we continue, let's spend a bit of time learning what comprises an
event:


Introduction to events
----------------------
When an event handler gets called, it gets passed two parameters; an instance
of the client (in this most cases, this is just ``self``) and the event that 
triggered the handler. So, what information can we get from the event? 
Analyse the table below.

    +-------------------------------------------------------------------------+
    | Event structure                                                         |
    +--------------------+----------------------------------------------------+
    | Item               | Description                                        |
    +====================+====================================================+
    | ``event.command``  | ``The IRC command. (ex:PRIVMSG)``                  |
    +--------------------+----------------------------------------------------+
    | ``event.source``   | ``The origin of the line (nick or server)``        |
    +--------------------+----------------------------------------------------+
    | ``event.target``   | ``The target of the event.                         |
    |                    | Either a nick, channel, or None.``                 |
    +--------------------+----------------------------------------------------+
    | ``event.params``   | ``Any additional parameters for the event.``       |
    +--------------------+----------------------------------------------------+
    | ``event.message``  | ``The message data associated with the event       |
    |                    | This is only available if it is a MessageEvent``.  |
    +--------------------+----------------------------------------------------+
    
    Learn more about events in the :ref:`events <ircutils-events>` 
    documentation.

So now that we have an understanding of what is made up of an event, let's put
it to good use. Since the echo bot is supposed to *echo*, let's make it do just
that. We'll use the event handler ``on_channel_message`` for this. It gets
activated when a message (``PRIVMSG``) is sent to an IRC channel::

    from ircutils import bot

    class EchoBot(bot.SimpleBot):
        
        def on_welcome(self, event):
            self.join("#ircutils")

        def on_channel_message(self, event):
            # The target of the event was the channel itself, and since we want
            # to send a message to the same channel, we use the same target.
            self.send_message(event.target, event.message)

Where we have it now, this bot will successfully do what we specified. 
Let's add some code to run it::

    from ircutils import bot

    class EchoBot(bot.SimpleBot):
        
        def on_welcome(self, event):
            self.join("#ircutils")

        def on_channel_message(self, event):
            self.send_message(event.target, event.message)
    

    if __name__ == "__main__":
        # Create an instance of the bot
        # We set the bot's nickname here
        echo = EchoBot("echo_bot") 
        
        # Let's connect to the host
        echo.connect("irc.freenode.com", 6667)
        
        # Start running the bot
        echo.start()


Kick it up a notch
------------------
Let's make it send an action whenever it joins a channel, and welcome 
anybody who joins::

    from ircutils import bot

    class EchoBot(bot.SimpleBot):
        
        def on_welcome(self, event):
            self.join("#ircutils")
        
        def on_join(self, event):
            if event.source != self.nickname:
                self.send_message(event.target, "Welcome, %s!" % event.source)
            else:
                self.send_action(event.target, "will echo everything you say.")
        
        def on_channel_message(self, event):
            self.send_message(event.target, event.message)
            

    if __name__ == "__main__":
        echo = EchoBot("echo_bot") 
        echo.connect("irc.freenode.com", 6667)
        echo.start()


Formatting IRC messages
-----------------------
.. note::
   If the channel you're on has ``+c`` in the mode active, no formatting will be
   available as the server automatically strips all of the tags.

See the :ref:`ircutils.format documentation <ircutils-format>` for a 
more in-depth coverage.

The ``ircutils.format`` module has numerous functions for formatting outgoing 
text, such as 
:func:`bold() <ircutils.format.bold>`,
:func:`underline() <ircutils.format.underline>`,
:func:`reversed() <ircutils.format.reversed>`, and
:func:`color() <ircutils.format.color>`. Here is a small example::

	from ircutils import bot, format
	
	class ExampleBot(bot.SimpleBot):
	
	    def on_welcome(self, event):
	        self.join("#ircutils")
	
	    def on_join(self, event):
	        if event.source == self.nickname:
	            message = format.bold("Hello bold and green world!")
	            message = format.color(message, format.GREEN)
	            self.send_message(event.target, message)

Essentially, when using the formatting functions, apply it to the message
before it's sent out.

Running multiple bots at once
-----------------------------
To take advantage of the asynchronous nature of IRCUtils, we have the ability
to run multiple bots at the same time. One common mistake is that people try
to do something like the following::

    # THIS WILL NOT WORK
    bot1.start()
    bot2.start()

When ``start()`` gets called, it runs an internal loop and so anything after the
call essentially gets ignored. To do this, we use the ``start_all()`` function.
For example, look at this block of code::

	from ircutils import bot, start_all
	
	
	class HelloBot(bot.SimpleBot):
	    
	    def on_welcome(self, event):
	        self.join("#ircutils")
	    
	    def on_message(self, event):
	        if event.message.startswith("hey"):
	            self.send_message(event.target, "Hello!")
	
	
	class GoodbyeBot(bot.SimpleBot):
	    
	    def on_welcome(self, event):
	        self.join("#ircutils")
	    
	    def on_message(self, event):
	        if event.message.startswith("goodbye"):
	            self.send_message(event.target, "Goodbye!")
	
	
	if __name__ == "__main__":
	    hello = HelloBot("hello_bot") 
	    goodbye = GoodbyeBot("goodbye_bot")
	    
	    hello.connect("irc.freenode.com", 6667)
	    goodbye.connect("irc.freenode.com", 6667)
	    
	    start_all()

As you can see, we set up two different bots, have them both connect, and then
instead of calling the ``start()`` methods on them, we simply use 
``start_all()`` which we imported.