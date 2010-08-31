=================
IRCUtils Tutorial
=================
This tutorial is designed to give you a small taste of what ``ircutils`` has to 
offer you in terms of IRC solutions. It assumes you already have knowledge in
the Python programming language. If you don't, it is in your best interest
to go through the `Python tutorial <http://docs.python.org/tutorial/>`_ first.
Note that ``ircutils`` is strongly object-oriented, being familiar with objects 
and object-oriented programming would work in your favor.



Getting warmed up
=================
Let's start off light and build an IRC bot step-by-step.
It'll be an IRC bot that that responds to any channel message with that 
same message. We'll call it `EchoBot`. First, since we're using ``ircutils`` to 
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

So here we have our first true introduction to events and event handlers. 
Before we continue, let's spend a bit of time learning what comprises an
event so we can properly use them:



Introduction to events
======================
Each line sent from the IRC server represents its own event. This information
is parsed to fill in the values for the event object. In some cases, these
single-line events are combined together to build more complex events that span
multiple lines of data from the server.

When an event handler gets called, it gets passed two parameters; an instance
of the client (in most cases, this is just ``self``) and the event that 
triggered the handler. So, what information can we get from the event? 
Analyse the table below.

    +-------------------------------------------------------------------------+
    | Event structure                                                         |
    +--------------------+----------------------------------------------------+
    | Item               | Description                                        |
    +====================+====================================================+
    | ``event.command``  | The IRC command. (ex:PRIVMSG)                      |
    +--------------------+----------------------------------------------------+
    | ``event.source``   | The origin of the line (nick or server)            |
    +--------------------+----------------------------------------------------+
    | ``event.target``   | The target of the event.                           |
    |                    | Either a nick, channel, or None.                   |
    +--------------------+----------------------------------------------------+
    | ``event.params``   | Any additional parameters for the event.           |
    +--------------------+----------------------------------------------------+
    | ``event.message``  | The message data associated with the event         |
    |                    | This is only available if it is a MessageEvent.    |
    +--------------------+----------------------------------------------------+
    
    Learn more about events in the :mod:`ircutils.events` documentation.

So now that we have an understanding of what is made up of an event, let's put
it to good use. Since the echo bot is supposed to *echo*, let's make it do just
that. We'll use the event handler ``on_channel_message`` for this. It gets
activated when a message (``PRIVMSG``) is sent to an IRC channel::

    from ircutils import bot

    class EchoBot(bot.SimpleBot):

        def on_channel_message(self, event):
            # The target of the event was the channel itself, and since we want
            # to send a message to the same channel, we use the same target.
            self.send_message(event.target, event.message)

Where we have it now, this bot will successfully do what we specified. 
Let's add some code to run it::

    from ircutils import bot

    class EchoBot(bot.SimpleBot):

        def on_channel_message(self, event):
            self.send_message(event.target, event.message)
    

    if __name__ == "__main__":
        # Create an instance of the bot
        # We set the bot's nickname here
        echo = EchoBot("echo_bot") 
        
        # Let's connect to the host
        echo.connect("irc.freenode.com")
        
        # Start running the bot
        echo.start()

.. note::
   To see a full list of built-in event listeners, look at the 
   :ref:`list-of-event-names`.

Joining a channel automatically
===============================
Let's tell it to connect to ``#ircutils`` once it receives the 
IRC welcome message. There are two ways of doing this. First, we could set up 
an ``on_welcome`` handler and have it explicitly join the channel, or we can 
specify channels to join through the ``connect()`` method. It takes in an 
argument (``channel``) that specifies which channel to join once the client
connects. Optionally, ``channel`` can be a list of channels.
::

    from ircutils import bot

    class EchoBot(bot.SimpleBot):

        def on_channel_message(self, event):
            self.send_message(event.target, event.message)
    
    if __name__ == "__main__":
        echo = EchoBot("echo_bot") 
        echo.connect("irc.freenode.com", channel=["#ircutils", "#some_channel"])
        echo.start()

By not explicitly specifying which channels to join in the bot's primary code,
it allows your bot to be more abstract and not forced to `have` to join the 
channels in every use. 



Joining a channel on command
============================
Next, let's say you want it to join a specific channel that `you` specify, via a
private message. Then, we'd set it up using the ``on_private_message`` handler::

	from ircutils import bot
	
	class EchoBot(bot.SimpleBot):
	
	    def on_channel_message(self, event):
	        self.send_message(event.target, event.message)
	
	    def on_private_message(self, event):
	        """ This handler gets called when a PRIVMSG is received that's
	        targeted to the bot. 
	        
	        """
	        # Parse the message
	        message = event.message.split()
	        command = message[0].upper()    # The command is the first word
	        params = message[1:]            # Any words after that are params
	        
	        # Determine what to do
	        if command == "JOIN":
	            self.join_channel(params[0])
	        elif command == "PART":
	            self.part_channel(params[0])
	
	
	if __name__ == "__main__":
	    echo = EchoBot("echo_bot") 
	    echo.connect("irc.freenode.com")
	    echo.start()

With the above code, we can tell the ``echo_bot`` to join a channel with the 
following command in your IRC client: ``/msg echo_bot JOIN #some_channel`` . 
You can also use similar syntax to command it to part a channel.



Formatting an IRC message
=========================
.. note::
   If the channel you're on has ``+c`` in the mode active, no formatting will be
   available as the server automatically strips all of the tags.

The :mod:`ircutils.format` module has numerous 
functions for formatting outgoing text, such as 
:func:`bold() <ircutils.format.bold>`,
:func:`underline() <ircutils.format.underline>`,
:func:`reversed() <ircutils.format.reversed>`, and
:func:`color() <ircutils.format.color>`. Here is a small example::

	from ircutils import bot, format
	
	class ExampleBot(bot.SimpleBot):
	
	    def on_join(self, event):
	        if event.source == self.nickname:
	            message = format.bold("Hello bold and green world!")
	            message = format.color(message, format.GREEN)
	            self.send_message(event.target, message)

	if __name__ == "__main__":
	    example_bot = ExampleBot("secure_color")
	    example_bot.connect("irc.freenode.com", channel="#ircutils")
	    example_bot.start()

Essentially, when using the formatting functions, apply it to the message
before it's sent out. Futhermore, the :mod:`ircutils.format` module also 
provides a function for stripping formatting: :func:`ircutils.format.filter`. 



Running multiple bots at once
=============================
To take advantage of the asynchronous nature of ``ircutils``, we have the 
ability to run multiple bots at the same time. One common mistake is that 
people try to do something like the following::

    # THIS WILL NOT WORK
    bot1.start()
    bot2.start()

When ``start()`` gets called, it runs an internal loop and so anything after the
call essentially gets ignored. To do this, we use the ``start_all()`` function.
For example, look at this block of code::

	from ircutils import bot, start_all
	
	
	class HelloBot(bot.SimpleBot):
	    
	    def on_channel_message(self, event):
	        if event.message.startswith("hey"):
	            self.send_message(event.target, "Hello!")
	
	
	class GoodbyeBot(bot.SimpleBot):
	    
	    def on_channel_message(self, event):
	        if event.message.startswith("goodbye"):
	            self.send_message(event.target, "Goodbye!")
	
	
	if __name__ == "__main__":
	    hello_bot = HelloBot("hello_bot") 
	    goodbye_bot = GoodbyeBot("goodbye_bot")
	    
	    hello_bot.connect("irc.freenode.com", channel="#ircutils")
	    goodbye_bot.connect("irc.freenode.com", channel="#ircutils")
	    
	    # Starts both in the same asynchronous loop
	    start_all()

In the above example, we set up two different bots, have them both connect, 
and then instead of calling the ``start()`` methods on them, we use 
``start_all()`` which we imported. This will ensure that both are run.



Connecting using SSL
====================
Using an SSL connection will ensure that the bot is securely connected to the
server. Typically, this isn't necessary; however, there are servers that
''require'' clients to be connected via SSL, and even some channels. Let's
look at the formatting example from above and make it connect to a server
using SSL encryption::

	    bot = ExampleBot("secure_color")
	    bot.connect("irc.freenode.com", use_ssl=True, channel="#ircutils")
	    bot.start()

As you can see above, the flag ``use_ssl`` is used in the ``connect()`` method
in order to enable its use. If a port number isn't specified, ``7000`` is used.
If running multiple bots at once, it doesn't matter whether they are SSL 
connections or regular connections. Mixing of the two is fine.



Sub-classing (extending) IRC bots
=================================
The ability to subclass already built bots is one of the strongest features of
having your bot be built as a class in the first place. It allows you to 
define and combine features however you wish. For example, let's start off
with this small and simple ``WelcomeBot``::

    # File: welcome.py
    from ircutils import bot, format
    
    class WelcomeBot(bot.SimpleBot):
    
        def on_join(self, event):
            if event.source != self.nickname:
                message = format.bold("Welcome, {0}!".format(event.source))
                self.send_message(event.target, message)

Now, let's say we want to add on to this bot, but we really don't want to mess
up what we have here. Instead, let's just extend it! Save the code above into
a file called ``welcome.py`` and then continue on with this::

    import welcome
    
    class WellRoundedBot(welcome.WelcomeBot):
        
        def on_part(self, event):
            message = "waves goodbye to {0}.".format(event.source)
            self.send_action(event.target, message)


By extending off of ``welcome.WelcomeBot``, we inherit the ``on_join`` handler.



Need more help?
===============
So you've gone through the tutorial, and something's still not clear to you? 
No problem! Just 
`file a request </projects/ircutils/newticket?component=Documentation>`_ 
for more documentation or contact a developer directly via email.