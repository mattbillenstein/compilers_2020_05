from wabbit.tokenize import tokenize
from .test_helpers import assert_expectations


def test_compound():
    with open("tests/Script/cond.wb") as file:
        text = file.read()

    result = tokenize(text)

    assert_expectations(
        result,
        [
            ["VAR", None],
            ["NAME", "x"],
            ["ASSIGN", None],
            ["MINUS", None],
            ["INTEGER", 3],
            ["SEMI", None],
            ##
            ["IF", None],
            ["NAME", "x"],
            ["GT", None],
            ["INTEGER", 0],
            ["LBRACE", None],
            #
            ["PRINT", None],
            ["NAME", "x"],
            ["SEMI", None],
            #
            ["RBRACE", None],
            ["ELSE", None],
            ["LBRACE", None],
            #
            ["PRINT", None],
            ["MINUS", None],
            ["NAME", "x"],
            ["SEMI", None],
            ["RBRACE", None],
        ],
    )

