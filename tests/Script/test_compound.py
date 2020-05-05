from wabbit.tokenize import tokenize
from .test_helpers import assert_expectations


def test_compound():
    with open("tests/Script/compound.wb") as file:
        text = file.read()

    result = tokenize(text)

    assert_expectations(
        result,
        [
            ["VAR", None],
            ["NAME", "a"],
            ["ASSIGN", None],
            ["INTEGER", 42],
            ["SEMI", None],
            ["VAR", None],
            ["NAME", "b"],
            ["ASSIGN", None],
            ["INTEGER", 37],
            ["SEMI", None],
            #
            ["NAME", "a"],
            ["ASSIGN", None],
            ["LBRACE", None],
            ["VAR", None],
            ["NAME", "temp"],
            ["ASSIGN", None],
            ["NAME", "b"],
            ["SEMI", None],
            ["NAME", "b"],
            ["ASSIGN", None],
            ["NAME", "a"],
            ["SEMI", None],
            ["NAME", "temp"],
            ["SEMI", None],
            ["RBRACE", None],
            ["SEMI", None],
            ##
            ["PRINT", None],
            ["NAME", "a"],
            ["SEMI", None],
            ##
            ["PRINT", None],
            ["NAME", "b"],
            ["SEMI", None],
            ##
            ["PRINT", None],
            ["LBRACE", None],
            ["INTEGER", 2],
            ["PLUS", None],
            ["INTEGER", 2],
            ["SEMI", None],
            ["INTEGER", 10],
            ["PLUS", None],
            ["INTEGER", 10],
            ["SEMI", None],
            ["RBRACE", None],
            #
            ["PLUS", None],
            ["LBRACE", None],
            ["INTEGER", 2],
            ["PLUS", None],
            ["INTEGER", 2],
            ["SEMI", None],
            ["INTEGER", 20],
            ["PLUS", None],
            ["INTEGER", 20],
            ["SEMI", None],
            ["RBRACE", None],
            ["SEMI", None],
        ],
    )

