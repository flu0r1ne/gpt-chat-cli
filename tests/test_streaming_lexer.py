import re
from typing import Optional, Tuple
from enum import Enum, auto
from dataclasses import dataclass

import pytest

from src.gpt_chat_cli.streaming_lexer import (
    MatchState,
    CodeFenceContext,
    _try_to_parse_code_fence,
    SinglePassStreamingLexer,
    Token,
    TokenType,
    TokenOrientation,
    make_text_token
)

def test_try_to_parse_code_fence():
    # Test valid cases
    valid_cases = [
        ("```python\nhe", CodeFenceContext(0, "python", 10)),
        ("  ```python\n", CodeFenceContext(2, "python", 12)),
        ("~~~python\n", CodeFenceContext(0, "python", 10)),
        ("   ~~~python\nmore", CodeFenceContext(3, "python", 13))
    ]


    for case, expected in valid_cases:
        result = _try_to_parse_code_fence(case)
        assert result[0] == MatchState.MATCH
        assert result[1] == expected

    # Test invalid cases
    invalid_cases = [
        "    ```python\n",
        "~``python\n",
        "```python ```\n",
        "~~~python ~~~\n",
    ]

    for case in invalid_cases:
        print(case)
        result = _try_to_parse_code_fence(case)
        assert result[0] == MatchState.MISMATCH

    # Test indeterminate case
    indeterminate_cases = [
        "```",
        "  ~~~",
    ]

    for case in indeterminate_cases:
        result = _try_to_parse_code_fence(case)
        assert result[0] == MatchState.INDETERMINATE

def _check_exact_lexing_matches( chunk_tokens, final_tokens ):

    lexer = SinglePassStreamingLexer()

    for ( chunk, expected_tokens ) in chunk_tokens:

        lexer.add_chunk( chunk )

        n_tokens_emitted = 0

        for i, token in enumerate(lexer.parse()):
            assert i < len(expected_tokens)
            assert expected_tokens[i] == token

            n_tokens_emitted += 1

        assert n_tokens_emitted == len(expected_tokens)

    lexer.finish()

    n_tokens_emitted = 0

    for i, token in enumerate(lexer.parse()):
        assert i < len(final_tokens)
        print(token)
        assert final_tokens[i] == token

        n_tokens_emitted += 1

    assert n_tokens_emitted == len(final_tokens)


def test_single_pass_lexing():

    cases = [
        ( 'Some text\n', [
            make_text_token( 'Some text\n' )
        ] ),
        ( 'More text\n', [
            make_text_token( 'More text\n' )
        ] ),
        ( '  Indented text\n', [
            make_text_token( '  Indented text\n' )
        ] ),
        ( '```python\n', [
            Token( TokenType.CODE_FENCE, TokenOrientation.BEGIN, 'python' )
        ] ),
        ( 'print("Hello")\n', [
            make_text_token( 'print("Hello")\n' )
        ] ),
        ( '```', [] ),
    ]

    final_tokens = [
        Token( TokenType.CODE_FENCE, TokenOrientation.END ),
        Token( TokenType.EOF, TokenOrientation.NONE ),
    ]

    _check_exact_lexing_matches( cases, final_tokens )

    cases = [
        ( '```java\nSome text\nMore ', [
            Token( TokenType.CODE_FENCE, TokenOrientation.BEGIN, 'java' ),
            make_text_token( 'Some text\n' ),
            make_text_token( 'More ' ),
        ] ),
        ( ' text\n```', [
            make_text_token( ' text\n' ),
        ] ),
        ( '\n', [
            Token( TokenType.CODE_FENCE, TokenOrientation.END )
        ]),
    ]

    final_tokens = [
        Token( TokenType.EOF, TokenOrientation.NONE ),
    ]

    _check_exact_lexing_matches( cases, final_tokens )

    cases = [
        ( '  ```java \n  Some text\n  More ', [
            Token( TokenType.CODE_FENCE, TokenOrientation.BEGIN, 'java' ),
            make_text_token( 'Some text\n' ),
            make_text_token( 'More ' ),
        ] ),
        ( '  text\n  ```', [
            make_text_token( '  text\n' ),
        ] ),
        ( '\n', [
            Token( TokenType.CODE_FENCE, TokenOrientation.END )
        ]),
    ]

    final_tokens = [
        Token( TokenType.EOF, TokenOrientation.NONE ),
    ]

    _check_exact_lexing_matches( cases, final_tokens )

    cases = [
        ( '  ``', []),
        ('` java \n  Some text\n  More ', [
            Token( TokenType.CODE_FENCE, TokenOrientation.BEGIN, 'java' ),
            make_text_token( 'Some text\n' ),
            make_text_token( 'More ' ),
        ] ),
        ( '  text\n  ```', [
            make_text_token( '  text\n' ),
        ] ),
        ( '\n', [
            Token( TokenType.CODE_FENCE, TokenOrientation.END )
        ]),
    ]

    final_tokens = [
        Token( TokenType.EOF, TokenOrientation.NONE ),
    ]

    _check_exact_lexing_matches( cases, final_tokens )

    # Ticks preceded by characters don't initiate a code block
    cases = [
        ( 'tick```java\nSome text\n', [
            make_text_token( 'tick```java\n' ),
            make_text_token( 'Some text\n' ),
        ] ),
    ]

    final_tokens = [
        Token( TokenType.EOF, TokenOrientation.NONE ),
    ]

    _check_exact_lexing_matches( cases, final_tokens )

    # Code blocks which are not terminated, terminate
    # at the end of the document
    cases = [
        ( '```java\nSome text\n', [
            Token( TokenType.CODE_FENCE, TokenOrientation.BEGIN, 'java' ),
            make_text_token( 'Some text\n' ),
        ] ),
    ]

    final_tokens = [
        Token( TokenType.CODE_FENCE, TokenOrientation.END ),
        Token( TokenType.EOF, TokenOrientation.NONE ),
    ]

    _check_exact_lexing_matches( cases, final_tokens )

