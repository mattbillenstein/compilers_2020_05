# test_interpret_from_source.py
# uses pytest

from collections import ChainMap
import os
import sys

root = os.path.join(__file__, "..", "..")
sys.path.insert(0, root)

from wabbit.interp import interpret
from wabbit.parse import parse_source


def test_simplest():
    env = ChainMap()
    env['capture_print'] = []
    source = """
        print 1;
    """
    model = parse_source(source)
    interpret(model, env)
    assert env['capture_print'] == [1]


def test_fact():
    with open("tests/Script/fact.wb") as f:
        source = f.read()
    model = parse_source(source)
    env = ChainMap()
    env['capture_print'] = []
    interpret(model, env)
    assert env['capture_print'] == [1, 2, 6, 24, 120, 720, 5040, 40320, 362880]
