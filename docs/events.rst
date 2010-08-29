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
	example_client.register_listener("chan_msg", ChannelMessageListener)
	example_client.events["chan_msg"].add_handler(my_handler)
   
   
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
| ``message``         | Any message.                                           |
+---------------------+--------------------------------------------------------+
| ``channel_message`` | Message directed to channel.                           |
+---------------------+--------------------------------------------------------+
| ``private_message`` | Direct private message.                                |
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


Examples
========
*Coming soon.*