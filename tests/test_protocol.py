"""Test classes and methods in ircutils.protocol"""

from ircutils import protocol as p


def test_IRCstr_lower():
    original_str = p.IRCstr("abCD[]^123")
    lower_str = "abcd{}^123"

    assert str(original_str.lower()) == lower_str


def test_IRCstr_upper():
    original_str = p.IRCstr("abCD[]^123")
    upper_str = "ABCD[]~123"

    assert str(original_str.upper()) == upper_str