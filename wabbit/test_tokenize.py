from wabbit.tokenize import tokenize, Token


def test_plus():
    source = """+"""
    assert next(tokenize(source)) == Token("PLUS", "+")
