import re
from typing import Generator
from typing import List
from typing import NamedTuple
from typing import Tuple
from typing import Union

import utils


class Token(NamedTuple):
    type_: str
    token: str

    def __repr__(self):
        return f"Token({self.type_}, '{self.token}')"


TokenStream = Generator[Token, None, None]


KEYWORDS = {
    "const",
    "var",
    "print",
    "break",
    "continue",
    "if",
    "else",
    "while",
    "true",
    "false",
}
TYPES = {"bool", "char", "int", "float"}
TOKEN_TYPES: List[Union[Tuple[str, str], Tuple[str, str, int]]] = [
    ("FLOAT", r"\d+\.\d*"),  # TODO: floats with nothing before the "."
    ("INTEGER", r"\d+"),  # Integer or decimal number, TODO: leading "."
    ("SEMICOLON", r";"),
    ("BOOL", r"(true|false)"),
    ("NAME", r"[_A-Za-z]([_A-Za-z0-9]+)?"),
    ("ADD", r"\+"),
    ("SUB", r"\-"),
    ("MUL", r"\*"),
    ("DIV", r"/"),
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

IGNORE = r"[ \n]"
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
            continue
        if text[:2] == "/*":
            text = text[text.find("*/") + len("*/") :]  # noqa
            continue

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
                        type_ = matched.upper()
                    if matched in TYPES:
                        type_ = "TYPE"
                yield Token(type_, matched)
                break
        else:
            raise RuntimeError(f"Unrecognized input: __{text[:10]}__...")


def test_tokenizer():
    test_cases = [
        ("+", [("ADD", "+")]),
        ("++", [("ADD", "+"), ("ADD", "+")]),
        ("+ +", [("ADD", "+"), ("ADD", "+")]),
        ("+!", [("ADD", "+"), ("LNOT", "!")]),
        (
            "(1 + 2)",
            [("LPAREN", "("), ("INTEGER", "1"), ("ADD", "+"), ("INTEGER", "2"), ("RPAREN", ")")],
        ),
        (
            "+ - * / < <= > >= == != && || !",
            [
                ("ADD", "+"),
                ("SUB", "-"),
                ("MUL", "*"),
                ("DIV", "/"),
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
        ("const CONST", [("CONST", "const"), ("NAME", "CONST")]),
        ("'a'", [("CHAR", "a")]),
        (r"'\xhh'", [("CHAR", r"\xhh")]),
        (r"'\n'", [("CHAR", r"\n")]),
        # (r"'\''", [("CHAR", "'")]),  # TODO
        (
            "var a int = 2;",
            [
                ("VAR", "var"),
                ("NAME", "a"),
                ("TYPE", "int"),
                ("ASSIGN", "="),
                ("INTEGER", "2"),
                ("SEMICOLON", ";"),
            ],
        ),
        ("/* COMMENT */+", [("ADD", "+")]),
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
