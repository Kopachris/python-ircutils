=================
ircutils.protocol
=================

.. automodule:: ircutils.protocol
   :members: filter_nick, is_channel, is_nick, parse_line, parse_prefix,
             parse_mode, strip_name_symbol, ip_to_ascii, ascii_to_ip


Channel class
=============
.. autoclass:: Channel
      
      .. attribute:: name
      
            The channel name.
      
      .. attribute:: user_list
      
            A list of users in this channel.