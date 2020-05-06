# test_script_models.py
# uses pytest

from collections import ChainMap
import os
import sys

root = os.path.join(__file__, "..", "..")
sys.path.insert(0, root)

import script_models as sm
from wabbit.interp import interpret


def test_expr1():
    env = ChainMap()
    env['capture_print'] = []
    assert interpret(sm.expr_model, {}) == 14
    interpret(sm.expr_model_a, env)
    assert env['capture_print'] == [14]


def test_model1():
    env = ChainMap()
    env['capture_print'] = []
    interpret(sm.model1, env)
    assert env['capture_print'] == [-10, 2.75, 1, 2]


def test_model2():
    env = ChainMap()
    env['capture_print'] = []
    interpret(sm.model2, env)
    assert env['capture_print'] == [6.28318]


def test_model3():
    env = ChainMap()
    env['capture_print'] = []
    interpret(sm.model3, env)
    assert env['capture_print'] == [2]


def test_model4():
    env = ChainMap()
    env['capture_print'] = []
    interpret(sm.model4, env)
    assert env['capture_print'] == [1, 2, 6, 24, 120, 720, 5040, 40320, 362880]


def test_model5():
    env = ChainMap()
    env['capture_print'] = []
    interpret(sm.model5, env)
    assert env['capture_print'] == [42, 37]
