import pytest
from wabbit.tokenize import tokenize
from tests.Script.test_helpers import assert_expectations


def test_logical_operators():
    source = """+ - * > / < >= == <= != && || !"""
    assert set(t.type for t in tokenize(source)) == {
        "PLUS",
        "MINUS",
        "TIMES",
        "DIVIDE",
        "LT",
        "LE",
        "GT",
        "GE",
        "EQ",
        "NE",
        "LAND",
        "LOR",
        "LNOT",
    }


def test_misc():
    source = "{(}) = ;"
    assert set(t.type for t in tokenize(source)) == {
        "LPAREN",
        "RPAREN",
        "RBRACE",
        "LBRACE",
        "SEMI",
        "ASSIGN",
    }


def test_reserved_words():
    source = "const var print break continue if else while true false"
    assert set(t.type for t in tokenize(source)) == {
        "CONST",
        "VAR",
        "TRUE",
        "FALSE",
        "ELSE",
        "WHILE",
        "IF",
        "CONTINUE",
        "BREAK",
        "PRINT",
    }


def test_integer():
    source = "234"
    assert next(tokenize(source)).type == "INTEGER"

    source = "0"
    assert next(tokenize(source)).type == "INTEGER"


def test_float():
    source = "234.1"
    assert next(tokenize(source)).type == "FLOAT"

    source = "232.0"
    assert next(tokenize(source)).type == "FLOAT"


def test_char():
    source = "'a'"
    result = tokenize(source)
    assert_expectations(result, [["CHAR", "a"]])

    source = "'\\xhh'"
    result = tokenize(source)
    assert_expectations(result, [["CHAR", "\\xhh"]])

    source = "'\\n'"
    result = tokenize(source)
    assert_expectations(result, [["CHAR", "\\n"]])

    source = "'\\'"
    result = tokenize(source)
    assert_expectations(result, [["CHAR", "\\"]])

    try:
        source = "'word'"
        result = tokenize(source)
        assert_expectations(result, [])
        pytest.fail("Multichar string did not cause error")
    except Exception:
        pass
