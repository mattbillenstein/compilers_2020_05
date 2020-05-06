import re

import utils

KEYWORDS = {"const", "var", "print", "break", "continue", "if", "else", "while", "true", "false"}
TYPES = {"bool", "char", "int", "float"}
TOKEN_TYPES = [
    ("NUMBER", r"\d+(\.\d*)?"),  # Integer or decimal number, TODO: leading "."
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


def _tokenize(text):
    while text:
        # Ignore white space
        if match := re.match(IGNORE, text):
            text = text[match.end() :]
            continue
        # Comments
        if text[:2] == "//":
            text = text[text.find("\n") :]
        if text[:2] == "/*":
            text = text[text.find("*/") :]

        for type_, *regexp in TOKEN_TYPES:
            # The tuple may specify the capture group as an optional third element.
            if len(regexp) == 2:
                regexp, group = regexp  # type: ignore
            else:
                [regexp], group = regexp, 0  # type: ignore
            if match := re.match(regexp, text):
                matched = match.string[match.start(group) : match.end(group)]  # type: ignore
                text = text[match.end() :]
                if type_ == "NAME":
                    if matched in KEYWORDS:
                        type_ = "KEYWORD"
                    if matched in TYPES:
                        type_ = "TYPE"
                yield type_, matched
                break
        else:
            raise RuntimeError(f"Unrecognized input: __{text[:10]}__...")


def tokenize(text):
    return list(_tokenize(text))


def test_tokenizer():
    test_cases = [
        ("+", [("OP", "+")]),
        ("++", [("OP", "+"), ("OP", "+")]),
        ("+ +", [("OP", "+"), ("OP", "+")]),
        ("+!", [("OP", "+"), ("LNOT", "!")]),
        (
            "(1 + 2)",
            [("LPAREN", "("), ("NUMBER", "1"), ("OP", "+"), ("NUMBER", "2"), ("RPAREN", ")")],
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
                ("NUMBER", "2"),
                ("SEMICOLON", ";"),
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
