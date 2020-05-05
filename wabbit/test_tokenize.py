from wabbit.tokenize import tokenize


def test_plus():
    source = """+"""
    assert next(tokenize(source)).value == "+"
