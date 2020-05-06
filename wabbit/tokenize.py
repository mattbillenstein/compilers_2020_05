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

IGNORE = " "
# Errors: Your lexer may optionally recognize and report the following
# error messages:
#
#      lineno: Illegal char 'c'
#      lineno: Unterminated character constant
#      lineno: Unterminated comment
#


# def print(*args):
#     pass


def tokenize(text):
    text = text.rstrip()
    while text:
        if match := re.match(IGNORE, text):
            text = text[match.end() :]
            continue

        for name, regexp in TOKENS:
            if match := re.match(regexp, text):
                yield name, match.string[: match.end()]
                text = text[match.end() :]
                break
        else:
            raise RuntimeError(f"Unrecognized input: __{text[:10]}__...")


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
