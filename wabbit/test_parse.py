import pytest
from wabbit.parse import WabbitParser
from wabbit.tokenize import tokenize
from wabbit.model import *
from tests.Script.test_helpers import assert_expectations


def test_parser_name():
    parser = WabbitParser()
    source = "2;"
    tokens = tokenize(source)

    assert parser.parse(tokens) == Statements([Integer(2)])


# def test_parser_basics():
#     source = "2.9 * 2.7"
#     tokens = tokenize(source)
#     parser = WabbitParser()

#     assert parser.parse(tokens) == BinOp("*", Float(2.9), Float(2.7))

#     source = "2 / 7"
#     tokens = tokenize(source)
#     parser = WabbitParser()

#     assert parser.parse(tokens) == BinOp("/", Integer(2), Integer(7))

#     source = "2 + 3 / 7"
#     tokens = tokenize(source)
#     parser = WabbitParser()

#     assert parser.parse(tokens) == BinOp(
#         "+", Integer(2), BinOp("/", Integer(3), Integer(7))
#     )
