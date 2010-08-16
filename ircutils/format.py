"""
    IRC text formatting.
    
    Author:       Evan Fosmark <me@evanfosmark.com>
    Description:  Tools for formatting text being sent outward. This includes
                  bold, underline, and reversed text. It also has the ability
                  to add color.
"""
import re

# Text formatting tags
BOLD = "\x02"
UNDERLINE = "\x1F"
REVERSED = "\x16"
NORMAL = "\x0F"
COLOR_TAG = "\x03"

# Color indicies
BLACK = "1"
NAVY_BLUE = "2"
GREEN = "3"
RED = "4"
BROWN = "5"
PURPLE = "6"
OLIVE = "7"
YELLOW = "8"
LIME_GREEN = "9"
TEAL = "10"
AQUA = "11"
BLUE = "12"
PINK = "13"
DARK_GRAY = "14"
LIGHT_GRAY = "15"
WHITE = "16"

# Filter modes
FILTER_ALL = 1
FILTER_BOLD = 2
FILTER_UNDERLINE = 4
FILTER_REVERSED = 8
FILTER_COLORS = 16



def filter(text, type=FILTER_ALL):
    """ Removes all of the formatting marks from ``text``. 
        Type can be either FILTER_ALL, FILTER_BOLD, FILTER_UNDERLINE, 
        FILTER_REVERSED, or FILTER_COLORS.
    """
    if type == FILTER_BOLD:
        return text.replace(BOLD, "")
    elif type == FILTER_UNDERLINE:
        return text.replace(UNDERLINE, "")
    elif type == FILTER_REVERSED:
        return text.replace(REVERSED, "")
    elif type == FILTER_COLORS:
        return re.sub("(\x03(\d+(,\d+)?)?)", "", text)
    else:
        return re.sub("(\x02|\x1F|\x16|\x0F|(\x03(\d+(,\d+)?)?)?)", "", text)


def bold(text):
    """ Causes the output text to be seen as bold in other clients. """
    return BOLD + text + BOLD

def underline(text):
    """ Causes output text to be seen as underlined in other clients. """
    return UNDERLINE + text + UNDERLINE

def reversed(text):
    """ Causes output text to be seen as reversed (color) in other clients. """
    return REVERSED + text + REVERSED

def color(text, foreground, background=None):
    """ Specifies a text color (and optionally a background color) for a piece
        of text being sent.
    """
    # TODO: Make sure format.color() is correct
    color = COLOR_TAG + foreground
    if background is not None:
        color += ",%s" % background
    return color + text + (COLOR_TAG * 3)