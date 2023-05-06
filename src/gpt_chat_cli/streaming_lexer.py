#
# SINGLE-PASS STREAMING LEXER
# ---------------------------
#
# This is a simple "streaming lexer" which is designed to provide real-time syntax highlighting.
# It consumes input from the LLM as it is produced and parses it efficiently, emitting tokens
# as soon as they are available.
#
# The language is a subset of markdown. GPT seems to sometimes emit markdown, although it is somewhat
# fickle and does not reliably emit most tokens. When responding to programming questions, it does
# prefer code blocks and code spans. Maybe this should not be surprising since programmers do tend
# to use markdown.
#
# For the design of this "streaming lexer," a subset of this markdown will be parsed. While I would like
# to expand its purview, I have limited capacity.
#
# Thus, for version 0.0.3 we will only consider fenced code blocks and code spans. Fenced code blocks will
# be passed off to pygments for syntax highlighting. Code spans will be highlighted a different color to
# differentiate them from the rest of the text.
#
# A custom lexer seems to be needed since I have not found a lexer which is able to emit tokens when they
# are guaranteed and no sooner. If this evolves, it may need to not completely follow the commonmark spec.
# The recommended algorithm to parse markdown follows a two-pass algorithm. Regardless, the goals of the
# syntax highlighting may differ from full parsing since it is highlighting the textual content rather
# than converting the markdown to HTML.
#
# Currently, the design is one which emits two kinds of tokens "text" and "delimiters." Text unsurprisingly
# contains text which can be displayed or passed on to another parser. The "delimiters" are meant to control
# style. Currently, all delimiters are parsed left-to-right. When the lexer emits a "beginning" delimiter,
# it must terminate it with an "end" delimiter.
#
# Here is an example:
# [PARAGRAPH BEGIN][TEXT "Here is some" ] [TEXT " text"] [CODE_SPAN BEGIN][TEXT "I'm in "][TEXT "the span"][CODE_SPAN END][PARAGRAPH END]
#
# Code fences "begin" block may contain an info string. This is stripped (as the markdown specification demands.)

####################################################
## AS OF 2023-05-06 ONLY CODE FENCES ARE IMPLEMENTED


from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Tuple, Iterator, Generator
import re

class TokenType(Enum):
    PARAGRAPH = auto()
    TEXT = auto()
    CODE_FENCE = auto()
    CODE_SPAN = auto()
    EOF = auto()

class TokenOrientation(Enum):
    NONE = auto()
    BEGIN = auto()
    END = auto()

@dataclass
class Token:
    type: TokenType
    orientation: TokenOrientation
    content: Optional[str] = None

def make_text_token( s : str ) -> Token:
    return Token(
        type = TokenType.TEXT,
        orientation = TokenOrientation.NONE,
        content = s
    )

class MatchState(Enum):
    MATCH = auto()
    INDETERMINATE = auto()
    MISMATCH = auto()

@dataclass
class CodeFenceContext:
    spacing : int
    info_string : str
    end : int

def _try_to_parse_code_fence( buffer, eof=False ) -> Tuple[MatchState, Optional[CodeFenceContext]]:
    '''
        Parse a code fence from a line boundary

        Example:

        ```python
          ```python
           ```python
           ~~~python

        Invalid:
            ```python [four spaces]
        ~``python
    '''

    # match between zero and three spaces, followed by a grouping of ` and ~
    fence_match = re.search(r"^( {0,3})([`~]{1,3})", buffer )

    if fence_match:
        fence_indicator = fence_match.group(2)

        # Ensure there isn't a mix of ` and ~
        if '`' in fence_indicator and '~' in fence_indicator:
            return ( MatchState.MISMATCH, None )

        remaining = buffer[fence_match.end():]

        if len(fence_indicator) != 3 and len(remaining) > 0:
            return ( MatchState.MISMATCH, None )

        if '\n' not in remaining and not eof:
            # wait for info string to accumulate
            return ( MatchState.INDETERMINATE, None )
        else:

            if eof:
                info_match = re.search(r"^([^`~\n]*)(?:\n|$)", remaining )
            else:
                info_match = re.search(r"^([^`~\n]*)\n", remaining )

            # info string cannot contain ^ or ~
            if not info_match:
                # info string cannot contain ` or ~
                return ( MatchState.MISMATCH, None )

            spaces = len(fence_match.group(1))
            info_string = info_match.group( 1 )

            # remove extra spaces
            info_string = info_string.strip()

            # end of match
            end = info_match.end() + fence_match.end()

            ctx = CodeFenceContext( spaces, info_string, end )

            return ( MatchState.MATCH, ctx )
    else:
        return ( MatchState.MISMATCH, None )

class SinglePassStreamingLexer( object ):
    _buffer : str
    _line_start : bool
    _eof : bool

    # "leaf" blocks
    _in_code_fence : bool
    _code_fence_spaces : int
    _in_paragraph : bool

    def __init__( self : "SinglePassStreamingLexer" ):
        self._buffer = ''
        self._line_start = True

        self._in_code_fence = False
        self._code_fence_spaces = 0
        self._in_paragraph = False
        self._eof = False

    def add_chunk( self : "SinglePassStreamingLexer", new_chunk : str ):
        self._buffer += new_chunk

    def finish( self : "SinglePassStreamingLexer" ):
        self._eof = True

    def _take_chunk( self : "SinglePassStreamingLexer", amount : int ):

        chunk = self._buffer[ : amount ]
        self._buffer = self._buffer[ amount : ]

        return chunk

    def _tokenize_text_until_newline( self : "SinglePassStreamingLexer" ):
        # we can take tokens until we hit a newline

        end = self._buffer.find('\n')

        if end == -1:
            l = len(self._buffer)

            if l != 0:
                self._line_start = False
                return make_text_token( self._take_chunk( l ) )
        else:
            self._line_start = True

            return make_text_token( self._take_chunk( end + 1 ) )

    def parse( self : "SinglePassStreamingLexer" ) -> Generator[Token, None, None]:

        while True:

            if len(self._buffer) == 0:
                if self._eof:

                    # terminate

                    if self._in_code_fence:
                        yield Token(
                            TokenType.CODE_FENCE,
                            TokenOrientation.END
                        )

                        self._in_code_fence = False

                    yield Token(
                        TokenType.EOF,
                        TokenOrientation.NONE
                    )

                    return
                else:
                    # Wait for more content
                    return

            if self._line_start:

                state, ctx = _try_to_parse_code_fence( self._buffer, eof=self._eof )

                if state == MatchState.INDETERMINATE and not self._eof:
                    # wait for more tokens to accumulate
                    return
                elif state == MatchState.MATCH:

                    chunk = self._take_chunk( ctx.end )

                    if self._in_code_fence:
                        # closing fences cannot contain info strings
                        # consider it in the code block
                        if len(ctx.info_string) != 0:
                            yield make_text_token( chunk )
                        else:
                            yield Token( TokenType.CODE_FENCE, TokenOrientation.END )
                            self._in_code_fence = False
                            self._code_fence_spaces = 0
                    else:

                        if self._in_paragraph:
                            yield Token( TokenType.PARAGRAPH, TokenOrientation.END )
                            self._in_paragraph = False

                        yield Token(
                            TokenType.CODE_FENCE,
                            TokenOrientation.BEGIN,
                            content = ctx.info_string
                        )

                        self._code_fence_spaces = ctx.spacing
                        self._in_code_fence = True

                    # if we get to this point, we are at the
                    # beginning of a line, restart parsing

                    continue

                # a mismatch occurred, but we're still at the beginning of
                # a line, emit regular text

                # TODO: add paragraph check
                if self._in_code_fence:
                    if len(self._buffer) < self._code_fence_spaces and \
                        not self._eof:
                        # wait for mare tokens
                        return

                    token = self._tokenize_text_until_newline()

                    # strip off beginning spaces
                    if token.content.startswith(' ' * self._code_fence_spaces):
                        token.content = token.content[self._code_fence_spaces:]

                    yield token

                    continue

                # FALLTHROUGH: tokenize text until newline then continue

            if self._in_code_fence:
                # tokenize text until next line
                pass

            # otherwise, emit a paragraph in the future
            token = self._tokenize_text_until_newline()
            yield token
            continue

