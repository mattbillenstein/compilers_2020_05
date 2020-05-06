from typing import NamedTuple
import re

import utils

TOKENS = [
    ("NUMBER", r"\d+(\.\d*)?"),  # Integer or decimal number, TODO: leading "."
    ("ASSIGN", r"="),  # Assignment operator
    ("SEMI", r";"),  # Statement terminator
    ("NAME", r"_[A-Za-z][_A-Za-z0-9]+"),  # Identifiers
    ("OP", r"[+\-*/]"),  # Arithmetic operators
    ("NEWLINE", r"\n"),  # Line endings
    ("SKIP", r"[ \t]+"),  # Skip over spaces and tabs
    ("KEYWORD", r"(const|var|print|break|continue|if|else|while|true|false) "),
    #     LPAREN   : '('
    #     RPAREN   : ')'
    #     LBRACE   : '{'
    #     RBRACE   : '}'
    # Operators
    ("LE", "<="),
    ("LT", "<"),
    ("GE", ">="),
    ("GT", ">"),
    ("EQ", "=="),
    ("NE", "!="),
    ("LNOT", "!"),
    ("LAND", "&&"),
    ("LOR", r"\|\|"),
    # Literals:
    #     CHAR    : 'a'     (a single character - byte)
    #               '\xhh'  (byte value)
    #               '\n'    (newline)
    #               '\''    (literal single quote)
    #
    # Comments:  To be ignored
    #      //             Skips the rest of the line
    #      /* ... */      Skips a block (no nesting allowed)
    ("MISMATCH", r"."),  # Any other character
]

# Errors: Your lexer may optionally recognize and report the following
# error messages:
#
#      lineno: Illegal char 'c'
#      lineno: Unterminated character constant
#      lineno: Unterminated comment
#


IGNORE = " "


class Token(NamedTuple):
    type: str
    value: str
    line: int
    column: int


# From https://docs.python.org/3/library/re.html#writing-a-tokenizer
def tokenize(code):
    keywords = {"IF", "THEN", "ENDIF", "FOR", "NEXT", "GOSUB", "RETURN"}
    tok_regex = "|".join("(?P<%s>%s)" % pair for pair in TOKENS)
    line_num = 1
    line_start = 0
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == "NUMBER":
            value = float(value) if "." in value else int(value)
        elif kind == "ID" and value in keywords:
            kind = value
        elif kind == "NEWLINE":
            line_start = mo.end()
            line_num += 1
            continue
        elif kind == "SKIP":
            continue
        elif kind == "MISMATCH":
            raise RuntimeError(f"{value!r} unexpected on line {line_num}")
        yield Token(kind, value, line_num, column)


def test_tokenizer():
    test_cases = [
        ("+", [("PLUS", "+")]),
        ("+!", [("PLUS", "+"), ("LNOT", "!")]),
        (
            "+ - * / < <= > >= == != && || !",
            [
                ("PLUS", "+"),
                ("MINUS", "-"),
                ("TIMES", "*"),
                ("DIVIDE", "/"),
                ("LT", "<"),
                ("LE", "<="),
                ("GT", ">"),
                ("GE", ">="),
                ("EQ", "=="),
                ("NE", "!="),
                ("LAND", "&&"),
                ("LOR", "||"),
                ("LNOT", "!"),
            ],
        ),
    ]
    for source, expected_tokens in test_cases:
        actual_tokens = list(tokenize(source))
        if actual_tokens != expected_tokens:
            utils.delta(expected_tokens, actual_tokens)
        assert actual_tokens == expected_tokens


# Main program to test on input files
def main(filename):
    with open(filename) as file:
        text = file.read()

    for tok in tokenize(text):
        print(tok)


if __name__ == "__main__":
    import sys

    main(sys.argv[1])
