from typing import Literal


class ColorCode:
    """A superclass to signal that color codes are strings"""

    BLACK: Literal[str]
    RED: Literal[str]
    GREEN: Literal[str]
    YELLOW: Literal[str]
    BLUE: Literal[str]
    MAGENTA: Literal[str]
    CYAN: Literal[str]
    WHITE: Literal[str]
    RESET: Literal[str]

    BLACK_BG: Literal[str]
    RED_BG: Literal[str]
    GREEN_BG: Literal[str]
    YELLOW_BG: Literal[str]
    BLUE_BG: Literal[str]
    MAGENTA_BG: Literal[str]
    CYAN_BG: Literal[str]
    WHITE_BG: Literal[str]

    BOLD: Literal[str]
    UNDERLINE: Literal[str]
    BLINK: Literal[str]


class VT100ColorCode(ColorCode):
    """A class containing VT100 color codes"""

    # Define the color codes
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'

    # Define the background color codes
    BLACK_BG = '\033[40m'
    RED_BG = '\033[41m'
    GREEN_BG = '\033[42m'
    YELLOW_BG = '\033[43m'
    BLUE_BG = '\033[44m'
    MAGENTA_BG = '\033[45m'
    CYAN_BG = '\033[46m'
    WHITE_BG = '\033[47m'

    # Define the bold, underline and blink codes
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'

class NoColorColorCode(ColorCode):
    """A class nullifying color codes to disable color"""

    # Define the color codes
    BLACK = ''
    RED = ''
    GREEN = ''
    YELLOW = ''
    BLUE = ''
    MAGENTA = ''
    CYAN = ''
    WHITE = ''
    RESET = ''

    # Define the background color codes
    BLACK_BG = ''
    RED_BG = ''
    GREEN_BG = ''
    YELLOW_BG = ''
    BLUE_BG = ''
    MAGENTA_BG = ''
    CYAN_BG = ''
    WHITE_BG = ''

    # Define the bold, underline and blink codes
    BOLD = ''
    UNDERLINE = ''
    BLINK = ''

def get_color_codes(no_color=False) -> ColorCode:
    if no_color:
        return NoColorColorCode
    else:
        return VT100ColorCode
