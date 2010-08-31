ircutils.client
===============
.. automodule:: ircutils.client


SimpleClient
-------------
.. autoclass:: SimpleClient
   :members: connect, execute, identify, join_channel, part_channel, disconnect,
             send_action, send_ctcp, send_ctcp_reply, send_message, send_notice,
             set_nickname, register_listener, start

   .. attribute:: nickname
         
         The nickname bound to the client. To set a new nickname, use the
         :func:`ircutils.client.SimpleClient.set_nickname` method.
		
   .. attribute:: filter_formatting
         
         By default, ``filter_formatting`` is set to true. This means that any
         messages received that contain formatting tags will have those tags
         removed.
      	   
   .. attribute:: channels
      	   
      	 A dict of channels which the bot has joined. The keys are the channel
      	 names and the values are :class:`ircutils.protocol.Channel` instances.
	
   .. attribute:: real_name
      	   
      	 Shows up when ``WHOIS`` data is queried. It is set to the web
      	 address to ``ircutils`` by default.
         
   .. attribute:: user
   	     
   	     The user ID. Typically this is set to the nickname; however, you
   	     explicitly set it before connecting.
      	 

Examples
--------
Here is a simple script that works with the IRC client in order to print 
messages::
	
	from ircutils import client
	
	
	def message_printer(client, event):
	    print "<{0}/{1}> {2}".format(event.source, event.target, event.message)
	    
	def notice_printer(client, event):
	    print "(NOTICE) {0}".format(event.message)
	
	
	# Create a SimpleClient instance
	my_client = client.SimpleClient(nick="client_name")
	
	# Add the event handlers
	my_client["channel_message"].add_handler(message_printer)
	my_client["notice"].add_handler(notice_printer)
	
	# Finish setting up the client
	my_client.connect("irc.freenode.com", channel="#ircutils")
	my_client.start()