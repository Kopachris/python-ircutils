===============
ircutils.events
===============
.. automodule:: ircutils.events


Event classes
=============
.. autoclass:: StandardEvent
   
   .. attribute:: source
         
         The source of the event. This will either be a user's nickname or it
         will be the server host.
   
   .. attribute:: target
         
         The target of the event. This will either be a user's nickname, a
         channel name, or ``None`` in cases where there is no target.d
   
   .. attribute:: command
         
         The IRC command. This will always be upper-cased.
         
   .. attribute:: params
         
         A list of additional parameters for the event. 
   
   .. attribute:: user
         
         The IRC user-id. This typically isn't used. If you are looking for 
         a way to reference the person, use their nickname found in ``source``.
         This may be ``None``.
   
   .. attribute:: host
         
         The host of the source.



.. autoclass:: MessageEvent

.. autoclass:: CTCPEvent


Event listeners
===============
Event listeners are used to allow for event handling. At each event caused
by a line from the server, the event listener's ``notify()`` method is called.
That method then analyses the event if it determines it matches the 
information constraints it has in place, it will activate its event handlers.

Let's adapt an example directly from the source code. It is an event 
listener that is looking for messages that's targeting a channel::
	
	from ircutils import client, events
	
	class ChannelMessageListener(events.EventListener):
	    
	    def notify(self, client, event):
	        if event.command == "PRIVMSG":
	            if protocol.is_channel(event.target):
	                self.activate_handlers(client, event)
	
	example_client = client.SimpleClient()
	example_client.register_listener("chan_msg", ChannelMessageListener())
	example_client["chan_msg"].add_handler(my_handler)
   
   
Event listener base class
-------------------------
.. autoclass:: EventListener
   :members:


Creating quick event listeners
------------------------------
Sometimes people just need a quick solution and don't want to build a class
by hand in order to accommodate some simple event condition. This is why
the :func:`ircutils.events.create_listener` function exists.

.. autofunction:: create_listener


Creating more complex event listeners
-------------------------------------
Due to ``create_listener()``'s limited support, there are times when a more
complex event listener needs to be created. 
Let's say, for example, we want to create an event listener that scrapes 
MOTD (message-of-the-day) data. First, since this doesn't fit in any event-type
that is built in, we need to create a ``MOTDEvent``. If we look at  
:rfc:`2182#page-48`, we can see what makes up the MOTD replies::

   375    RPL_MOTDSTART
          ":- <server> Message of the day - "
   372    RPL_MOTD
          ":- <text>"
   376    RPL_ENDOFMOTD
          ":End of MOTD command"

We see that A MOTD is made up of first a line that has the server name, 
and then any number of lines that has the actual data. 
Let's use this to build our event::

    # bot and format are use later
    from ircutils import events, bot, format 
    
    class MOTDReplyEvent(events.Event):
        def __init__(self):
            self.server = None
            self.text = []

Next, we'll write the actual listener. We'll use the ``notify()`` method in 
order to fill in the values for the reply event. Then, once we get an
``RPL_ENDOFMOTD`` command from the server, we know we're done collecting the
data and we can dispatch the event::

	class MOTDReplyListener(events.EventListener):
	    
	    def __init__(self):
	        events.ReplyListener.__init__(self)
	        self._motd_event = MOTDReplyEvent()
	    
	    def notify(self, client, event):
	        if event.command == "RPL_MOTDSTART":
	            # :- <server> Message of the day - 
	            server = event.params[0][2:].split()[0]
	            self._motd_event.server = server
	        elif event.command =="RPL_MOTD":
	            # :- <text>
	            text = format.filter(event.params[0][2:])
	            self._motd_event.text.append(text)
	        elif event.command == "RPL_ENDOFMOTD":
	            # :End of MOTD command
	            self.activate_handlers(client, self._motd_event)
	            self._motd_event = MOTDReplyEvent()

Simple enough. In the ``__init__`` method we create the instance of the
``MOTDReplyEvent`` and then it gets populated, and eventually the listener
activates its handlers. 

Let's write a bot to take advantage of this. It will collect the MOTD data,
print it out, and then disconnect from the server::

	class MOTDBot(bot.SimpleBot):
	    
	    def on_motd(self, motd_event):
	        print "=" * 80
	        print "[{0}] Message of the day:".format(motd_event.server)
	        print "=" * 80
	        for line in motd_event.text:
	            print line
	        print "=" * 80
	        self.quit()


But wait, where did this ``on_motd`` handler come from? It isn't in the list of
built in handlers. We need to register the listener so we can use it. Look at 
this startup code to see::

	if __name__ == "__main__":
	    motd_bot = MOTDBot("motd_bot")
	    motd_bot.connect("irc.example.com")
	    motd_bot.register_listener("motd", MOTDReplyListener())
	    motd_bot.start()

At the point where ``register_listener`` is called, `motd` is set as the name
of the event, so through a bot, it is accessed through the ``on_motd`` method.

.. _list-of-event-names:

List of built-in listeners
==========================

The following are lists of built-in handlers for 
:class:`ircutils.client.SimpleClient` and :class:`ircutils.bot.SimpleBot`. To
create a handler using the ``SimpleBot``, just create a method with a 
signature like this: ``def on_<name>(self, event):`` where ``<name>`` is the
event name listed below.

+---------------------+--------------------------------------------------------+
| Name                | Description                                            |
+=====================+========================================================+
|                                                                              |
+------------------------------------------------------------------------------+
| **Listeners that use**                                                       |
| :class:`ircutils.events.StandardEvent`:                                      |
+---------------------+--------------------------------------------------------+
|``any``              | Any event will be caught by this.                      |
+---------------------+--------------------------------------------------------+
|``welcome``          | IRC welcome message.                                   |
+---------------------+--------------------------------------------------------+
|``ping``             | PING query. Auto-handled.                              |
+---------------------+--------------------------------------------------------+
|``invite``           | INVITE request.                                        |
+---------------------+--------------------------------------------------------+
|``kick``             | A user has been kicked.                                |
+---------------------+--------------------------------------------------------+
|``join``             | A user has joined.                                     |
+---------------------+--------------------------------------------------------+
|``quit``             | A user has quit.                                       |
+---------------------+--------------------------------------------------------+
|``part``             | A user has parted a channel.                           |
+---------------------+--------------------------------------------------------+
|``nick_change``      | A user has parted a channel.                           |
+---------------------+--------------------------------------------------------+
|``error``            | An error has occurred!                                 |
+---------------------+--------------------------------------------------------+
|                                                                              |
+------------------------------------------------------------------------------+
| **Listeners that use**                                                       |
| :class:`ircutils.events.MessageEvent`:                                       |
+---------------------+--------------------------------------------------------+
| ``message``         | Any (PRIVMSG-based) message.                           |
+---------------------+--------------------------------------------------------+
| ``channel_message`` | Message directed to channel.                           |
+---------------------+--------------------------------------------------------+
| ``private_message`` | Direct private message.                                |
+---------------------+--------------------------------------------------------+
| ``notice``          | Any (NOTICE-based) message.                            |
+---------------------+--------------------------------------------------------+
| ``channel_notice``  | Notice directed to a channel.                          |
+---------------------+--------------------------------------------------------+
| ``private_notice``  | A direct private notice.                               |
+---------------------+--------------------------------------------------------+
|                                                                              |
+------------------------------------------------------------------------------+
| **Listeners that use**                                                       |
| :class:`ircutils.events.CTCPEvent`:                                          |
+---------------------+--------------------------------------------------------+
| ``ctcp``            | Any CTCP event.                                        |
+---------------------+--------------------------------------------------------+
| ``ctcp_action``     | An action has been received.                           |
+---------------------+--------------------------------------------------------+
| ``ctcp_userinfo``   | USERINFO request.                                      |
+---------------------+--------------------------------------------------------+
| ``ctcp_clientinfo`` | CLIENTINFO request.                                    |
+---------------------+--------------------------------------------------------+
| ``ctcp_version``    | VERSION request. Auto-handled.                         |
+---------------------+--------------------------------------------------------+
| ``ctcp_ping``       |                                                        |
+---------------------+--------------------------------------------------------+
| ``ctcp_error``      | A CTCP error has occurred.                             |
+---------------------+--------------------------------------------------------+
| ``ctcp_time``       | Time bounce request.                                   |
|                     | This is auto-handled.                                  |
+---------------------+--------------------------------------------------------+
| ``dcc``             | A request for a DCC action.                            |
+---------------------+--------------------------------------------------------+
|                                                                              |
+------------------------------------------------------------------------------+
| **Listeners that wait for replies:**                                         |
+---------------------+--------------------------------------------------------+
| ``reply``           | Any reply event                                        |
+---------------------+--------------------------------------------------------+
| ``name_reply``      | A name reply has been received.                        |
+---------------------+--------------------------------------------------------+
| ``name_reply``      | A name reply has been received.                        |
+---------------------+--------------------------------------------------------+
| ``list_reply``      | A reply to the LIST command.                           |
+---------------------+--------------------------------------------------------+
| ``error_reply``     | Something you did caused an error                      |
|                     | to be sent as a reply.                                 |
+---------------------+--------------------------------------------------------+

.. note:: Reply events are typically much more complex and often don't rely on
   the three main event types described, and as such require 
   their own event type. It is standard practice to have this event type nested 
   within the event listener code. 
