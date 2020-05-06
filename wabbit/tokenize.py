import re
from typing import Generator
from typing import List
from typing import Tuple
from typing import Union

import utils

Token = Tuple[str, str]
TokenStream = Generator[Token, None, None]


KEYWORDS = {"const", "var", "print", "break", "continue", "if", "else", "while", "true", "false"}
TYPES = {"bool", "char", "int", "float"}
TOKEN_TYPES: List[Union[Tuple[str, str], Tuple[str, str, int]]] = [
    ("FLOAT", r"\d+\.\d*"),  # TODO: floats with nothing before the "."
    ("INTEGER", r"\d+"),  # Integer or decimal number, TODO: leading "."
    ("SEMICOLON", r";"),
    ("NAME", r"[_A-Za-z]([_A-Za-z0-9]+)?"),
    ("OP", r"[+\-*/]"),
    ("NEWLINE", r"\n"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", "{"),
    ("RBRACE", "}"),
    ("LE", "<="),
    ("LT", "<"),
    ("GE", ">="),
    ("GT", ">"),
    ("EQ", "=="),
    ("ASSIGN", r"="),
    ("NE", "!="),
    ("LNOT", "!"),
    ("LAND", "&&"),
    ("LOR", r"\|\|"),
    ("CHAR", r"'(\\?[^\\]|\'[^\\]|\\x[^\\]{2})'", 1),
]

IGNORE = " "
# Errors: Your lexer may optionally recognize and report the following
# error messages:
#
#      lineno: Illegal char 'c'
#      lineno: Unterminated character constant
#      lineno: Unterminated comment
#


def tokenize(text: str) -> TokenStream:
    while text:
        # Ignore white space
        if match := re.match(IGNORE, text):
            text = text[match.end() :]  # noqa
            continue
        # Comments
        if text[:2] == "//":
            text = text[text.find("\n") :]  # noqa
        if text[:2] == "/*":
            text = text[text.find("*/") :]  # noqa

        for type_, *regexp in TOKEN_TYPES:
            # The tuple may specify the capture group as an optional third element.
            if len(regexp) == 2:
                regexp, group = regexp  # type: ignore
            else:
                [regexp], group = regexp, 0  # type: ignore
            if match := re.match(regexp, text):  # type: ignore
                matched = match.string[match.start(group) : match.end(group)]  # type: ignore  # noqa
                text = text[match.end() :]  # noqa
                if type_ == "NAME":
                    if matched in KEYWORDS:
                        type_ = "KEYWORD"
                    if matched in TYPES:
                        type_ = "TYPE"
                yield type_, matched
                break
        else:
            raise RuntimeError(f"Unrecognized input: __{text[:10]}__...")


def test_tokenizer():
    test_cases = [
        ("+", [("OP", "+")]),
        ("++", [("OP", "+"), ("OP", "+")]),
        ("+ +", [("OP", "+"), ("OP", "+")]),
        ("+!", [("OP", "+"), ("LNOT", "!")]),
        (
            "(1 + 2)",
            [("LPAREN", "("), ("INTEGER", "1"), ("OP", "+"), ("INTEGER", "2"), ("RPAREN", ")")],
        ),
        (
            "+ - * / < <= > >= == != && || !",
            [
                ("OP", "+"),
                ("OP", "-"),
                ("OP", "*"),
                ("OP", "/"),
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
        ("frog", [("NAME", "frog")]),
        ("const CONST", [("KEYWORD", "const"), ("NAME", "CONST")]),
        ("'a'", [("CHAR", "a")]),
        (r"'\xhh'", [("CHAR", r"\xhh")]),
        (r"'\n'", [("CHAR", r"\n")]),
        # (r"'\''", [("CHAR", "'")]),  # TODO
        (
            "var a int = 2;",
            [
                ("KEYWORD", "var"),
                ("NAME", "a"),
                ("TYPE", "int"),
                ("ASSIGN", "="),
                ("INTEGER", "2"),
                ("SEMICOLON", ";"),
            ],
        ),
    ]
    for source, expected_tokens in test_cases:
        actual_tokens = list(tokenize(source))
        if actual_tokens != expected_tokens:
            utils.print_diff(expected_tokens, actual_tokens)
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
