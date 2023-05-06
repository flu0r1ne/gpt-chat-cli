from pygments import highlight
from pygments.lexer import Lexer
from pygments.formatter import Formatter
from pygments.lexers import (
    get_lexer_by_name, get_all_lexers, guess_lexer,
    find_lexer_class_by_name
)
from pygments.formatters import (
    TerminalFormatter,
    NullFormatter
)

from dataclasses import dataclass
from typing import Optional
from pygments.util import ClassNotFound

from .streaming_lexer import (
    SinglePassStreamingLexer,
    Token,
    TokenType,
    TokenOrientation
)

from .color import (
    get_color_codes,
    ColorCode,
)

# Guessing languages takes time ...
# Assume these are our candidates since
# they likely cover upward of 90% of
# usage
GUESSABLE_LANGUAGES = [
    'html',
    'python',
    'java',
    'python2',
    'c++',
    'javascript',
    'c#',
    'sql',
    'c',
    'php',
    'go',
    'swift',
    'kotlin',
    'ruby',
    'typescript',
    'scala',
    'r',
    'rust',
    'css',
    'perl',
    'make',
    'text'
]

def guess_lexer( text : str, **options ):
    '''
    Guess the lexer in use from GUESSABLE_LANGUAGES.

    Uses very primitive heuristics and is not very good.
    '''

    best_lexer = [0.0, None]

    for lexer_name in GUESSABLE_LANGUAGES:

        lexer = find_lexer_class_by_name(lexer_name)

        rv = lexer.analyse_text(text)

        if rv == 1.0:
            return lexer(**options)
        if rv > best_lexer[0]:
            best_lexer[:] = (rv, lexer)

    if not best_lexer[0] or best_lexer[1] is None:

        raise ClassNotFound('no lexer matching the text found')

    return best_lexer[1](**options)

@dataclass
class CodefenceContext:
    language: str
    lexer : Lexer
    formatter : Formatter
    buffer : str = ''
    eof : bool = False

    def may_guess_language( self : "CodefenceContext" ):

        if self.eof:
            return True

        MIN_CHARACTERS = 150
        MIN_LINES = 2

        return (
            len(self.buffer) > MIN_CHARACTERS and
            self.buffer.count('\n') > MIN_LINES
        )

    def get_highlighted_lines(self : "CodefenceContext"):

        if self.language is None:
            if self.may_guess_language():

                lexer = guess_lexer( self.buffer )

                self.language = lexer.name
                self.lexer = lexer

            else:
                return None


        idx = self.buffer.rfind('\n')

        if idx == -1:
            return None
        else:
            lines = self.buffer[:idx+1]
            self.buffer = self.buffer[idx+1:]

            highlighted = highlight(
                lines,
                self.lexer,
                self.formatter,
            )

            return highlighted

class ChatColorizer( object ):

    lexer : SinglePassStreamingLexer
    formatter : Formatter
    cf_ctx : Optional[CodefenceContext]
    color_code : ColorCode
    text_emitted: bool

    def __init__( self : "ChatColorizer", no_color = False ):
        self.lexer = SinglePassStreamingLexer()

        self.cf_ctx = None

        if no_color:
            self.formatter = NullFormatter()
        else:
            self.formatter = TerminalFormatter()

        self.color_code = get_color_codes( no_color=no_color )
        self.text_emitted = False

    def add_chunk( self : "ChatColorizer", chunk : str ):
        self.lexer.add_chunk( chunk )

    def print( self : "ChatColorizer" ):

        for token in self.lexer.parse():

            if token.type == TokenType.EOF:
                break

            if token.type == TokenType.CODE_FENCE:

                if not self.text_emitted:
                    print()
                    self.text_emitted = True

                if token.orientation == TokenOrientation.BEGIN:
                    assert self.cf_ctx is None

                    lang = token.content

                    try:
                        lexer = get_lexer_by_name(lang)
                    except ClassNotFound:
                        # try to guess it
                        lang = None
                        lexer = None

                    self.cf_ctx = CodefenceContext(lang, lexer, self.formatter)

                else:
                    assert self.cf_ctx is not None

                    self.cf_ctx.eof = True

                    highlighted = self.cf_ctx.get_highlighted_lines()

                    if highlighted:
                        print( highlighted, end='', flush=True )

                    self.cf_ctx = None

                # Add extra \n to either side of a chunk
                print(f'{self.color_code.WHITE}```{self.color_code.RESET}', flush=True)

                continue

            if self.cf_ctx:

                self.cf_ctx.buffer += token.content
                highlighted = self.cf_ctx.get_highlighted_lines()

                if highlighted:
                    print( highlighted, end='', flush=True )

            else:

                print( f'{self.color_code.WHITE}{token.content}{self.color_code.RESET}', end='', flush=True )
                self.text_emitted = True


    def finish( self : "ChatColorizer" ):
        self.lexer.finish()
