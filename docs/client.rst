ircutils.client
===============
.. automodule:: ircutils.client

d

SimpleClient
-------------
.. autoclass:: SimpleClient
   :members: connect, execute, identify, join_channel, part_channel, quit,
             register_listener, send_action, send_ctcp, send_ctcp_reply,
             send_message, send_notice, set_nickname, start

   .. attribute:: nickname
         
         The nickname bound to the client. To set a new nickname, use the
         :func:`ircutils.client.SimpleClient.set_nickname` method.
         
   .. attribute:: user
   	     
   	     The user ID. Typically this is set to the nickname; however, you
   	     explicitly set it before connecting.
		
   .. attribute:: filter_formatting
         
         By default, ``filter_formatting`` is set to true. This means that any
         messages received that contain formatting tags will have those tags
         removed.
	
   .. attribute:: real_name
      	   
      	 Shows up when ``WHOIS`` data is queried. It is set to the web
      	 address to ``ircutils`` by default.
      	   
   .. attribute:: channels
      	   
      	 A dict of channels which the bot has joined. The keys are the channel
      	 names and the values are :class:`ircutils.protocol.Channel` instances.
      	 

Examples
--------
*Currently none.*