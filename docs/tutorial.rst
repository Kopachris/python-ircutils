The 5-Minute Tutorial
=====================

Let's start off with something simple. 
It'll be an IRC bot that that simply responds to any channel message with that 
same message. We'll call it `EchoBot`. 

First, since we're using IRCUtils to make a bot, we'll need to import the proper 
module::

    from ircutils import bot

Next, we'll use the SimpleBot class to build upon::

    from ircutils import bot

    class EchoBot(bot.SimpleBot):
        pass

    if __name__ == "__main__":
        echo = EchoBot("echobot")
        echo.connect("irc.freenode.com")
        echo.start()

Right now, we actually have a working IRC bot; however, it doesn't do anything 
other than connect to the server. Let's tell it to connect to #ircutils once it 
receives the IRC welcome message::

    from ircutils import bot

    class EchoBot(bot.SimpleBot):
        
        def on_welcome(self, event):
            self.join("#ircutils")

    if __name__ == "__main__":
        echo = EchoBot("echobot")
        echo.connect("irc.freenode.com")
        echo.start()

Finally, let's provide a handler that any time it recieves a message on a 
channel, it outputs that same message to that same channel::

    from ircutils import bot

    class EchoBot(bot.SimpleBot):
        
        def on_welcome(self, event):
            self.join("#ircutils")

        def on_channel_message(self, event):
            self.send_message(event.target, event.message)

    if __name__ == "__main__":
        echo = EchoBot("echobot")
        echo.connect("irc.freenode.com")
        echo.start()

Done! This bot will successfully do what we specified. Run it and make sure 
everything is working! But hey, that's a bit boring. Let's make it send an 
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

    if __name__ == "__main__":
        echo = EchoBot("echobot")
        echo.connect("irc.freenode.com")
        echo.start()

That's it! 
