# test_script_models.py
# uses pytest

import os
import sys

root = os.path.join(__file__, "..", "..")
sys.path.insert(0, root)


from wabbit.tokenize import tokenize


def test_names():
    tokens = tokenize("abc _ab3 ab_")
    result = [(tok.type, tok.value) for tok in tokens]
    assert result == [("NAME", "abc"), ("NAME", "_ab3"), ("NAME", "ab_")]


def test_keywords():
    tokens = tokenize("const var print break continue")
    result = [tok.type for tok in tokens]
    assert result == ["CONST", "VAR", "PRINT", "BREAK", "CONTINUE"]

    tokens = tokenize("if else while true false")
    result = [tok.type for tok in tokens]
    assert result == ["IF", "ELSE", "WHILE", "TRUE", "FALSE"]


def test_floats():
    tokens = tokenize("123. 1.23 .123")
    assert all(tok.type == "FLOAT" for tok in tokens)


def test_integers():
    tokens = tokenize("123 1   34")
    assert all(tok.type == "INTEGER" for tok in tokens)


def test_comparisons():
    text = "> >= < <= == !="
    tokens = tokenize(text)
    assert text.split(" ") == [tok.value for tok in tokens]

    tokens = tokenize(text)
    assert [tok.type for tok in tokens] == ["GT", "GE", "LT", "LE", "EQ", "NE"]


def test_logical():
    text = "&& ||"
    tokens = tokenize(text)
    assert text.split(" ") == [tok.value for tok in tokens]

    tokens = tokenize(text)
    assert [tok.type for tok in tokens] == ["LAND", "LOR"]


def test_math_ops():
    text = "+ - / * ="
    tokens = tokenize(text)
    assert text.split(" ") == [tok.value for tok in tokens]

    tokens = tokenize(text)
    assert [tok.type for tok in tokens] == [
        "PLUS",
        "MINUS",
        "DIVIDE",
        "TIMES",
        "ASSIGN",
    ]


def test_symbols():
    text = "; ( ) { }"
    tokens = tokenize(text)
    assert text.split(" ") == [tok.value for tok in tokens]

    tokens = tokenize(text)
    assert [tok.type for tok in tokens] == [
        "SEMI",
        "LPAREN",
        "RPAREN",
        "LBRACE",
        "RBRACE",
    ]


def test_eol_comments():
    text = "a = 3 // this is a comment"
    tokens = tokenize(text)
    result = [tok.type for tok in tokens]
    assert result == ["NAME", "ASSIGN", "INTEGER"]


fake_program_with_comments = """
/* This is a
multi line comment */
42
/**** this is a single line comment ****/ a
"""


def test_multiline_comment():
    tokens = tokenize(fake_program_with_comments)
    assert [tok.type for tok in tokens] == ["INTEGER", "NAME"]


def test_char():
    tokens = tokenize("'é' 'a' ")
    assert [(tok.type, tok.value) for tok in tokens] == [
        ("CHAR", "é"),
        ("CHAR", "a"),
    ]


def test_dot():
    tokens = tokenize("x.y")
    assert [tok.type for tok in tokens] == ['NAME', 'DOT', 'NAME']
