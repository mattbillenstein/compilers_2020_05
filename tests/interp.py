import sys
from io import StringIO
from unittest.mock import patch

import clint
import pytest

from wabbit.format_json import format_json
from wabbit.interp import interpret_program
from wabbit.parse import Parser
from wabbit.tokenize import tokenize
from utils import print_source


def green(s):
    return clint.textui.colored.green(s, always=True, bold=True)


cases = [
    ("print 1 + 1;", ["2"]),
    ("print 1 + 2 * 3;", ["7"]),
    ("print 1 + 2 * -3;", ["-5"]),
    ("print 2 + 3 * -4;", ["-10"]),
    ("print -2 + 3;", ["1"]),
    ("print 2.0 - 3.0 / -4.0;", ["2.75"]),
    (
        """
const pi = 3.14159;
var tau float;
tau = 2.0 * pi;
print tau;
""",
        ["6.28318"],
    ),
    (
        """
var a int = 2;
var b int = 3;
if a < b {
    print a;
} else {
    print b;
}
""",
        ["2"],
    ),
    (
        """
const n = 4;
var x int = 1;
var fact int = 1;
while x < n {
    fact = fact * x;
    print fact;
    x = x + 1;
};
""",
        ["1", "2", "6"],
    ),
]


@pytest.mark.parametrize("source,expected", cases)
def test(source, expected):
    actual = interpret(source)
    assert actual == expected


def interpret(source):
    io = StringIO()
    with patch.object(sys, "stdout", io):
        statements = Parser(tokenize(source)).statements()
        interpret_program(statements)
    io.seek(0)
    return io.getvalue().splitlines()


def describe_failure(source, expected, actual):
    print(flush=True)
    print_source(source)

    print("\nExpected:")
    print("---------")
    for line in expected:
        print(line)

    print("\nActual:")
    print("-------")
    for line in actual:
        print(line)

    print("\nParser output:")
    print("--------------")
    print(format_json(Parser(tokenize(source)).statements()))


if __name__ == "__main__":
    for source, expected in cases:
        actual = interpret(source)
        if actual == expected:
            print(green("."), end="")
        else:
            describe_failure(source, expected, actual)
    print()
