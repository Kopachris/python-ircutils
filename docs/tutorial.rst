Tutorial
=====================
Let's start off with something simple. 


Getting warmed up
-----------------
It'll be an IRC bot that that simply responds to any channel message with that 
same message. We'll call it `EchoBot`. 

First, since we're using IRCUtils to make a bot, we'll need to import the proper 
module::

    from ircutils import bot

Next, we'll use the SimpleBot class to build upon::

    from ircutils import bot

    class EchoBot(bot.SimpleBot):
        # The bot is currently empty
        # We'll add event handlers next!
        pass

Right now, we actually have a working IRC bot; however, it isn't able to respond
to any events since we haven't added any event handlers.
Let's tell it to connect to #ircutils once it receives the IRC welcome message::

    from ircutils import bot

    class EchoBot(bot.SimpleBot):
        
        def on_welcome(self, event):
            self.join("#ircutils")

Finally, let's provide a handler that any time it recieves a message on a 
channel, it outputs that same message to that same channel::

    from ircutils import bot

    class EchoBot(bot.SimpleBot):
        
        def on_welcome(self, event):
            self.join("#ircutils")

        def on_channel_message(self, event):
            self.send_message(event.target, event.message)

Done! This bot will successfully do what we specified. Let's add some code to
run it::

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
But hey, that's a bit boring. Let's make it send an 
action whenever it joins a channel, and welcome anybody who joins::

    from ircutils import bot

    class EchoBot(bot.SimpleBot):
        
        def on_welcome(self, event):
            self.join("#ircutils")
        
        def on_join(self, event):
            if event.source != self.nickname: # don't want to welcome ourselves
                self.send_message(event.target, "Welcome, %s!" % event.source)
            else:
                self.send_action(event.target, "will echo everything you say.")
        
        def on_channel_message(self, event):
            self.send_message(event.target, event.message)

That's it! 
