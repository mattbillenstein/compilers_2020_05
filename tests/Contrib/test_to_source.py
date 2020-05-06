# test_script_models.py
# uses pytest

import os
import sys

root = os.path.join(__file__, "..", "..")
sys.path.insert(0, root)

import script_models as sm
from wabbit.model import to_source


def remove_unwanted(source):
    """To make the comparison robust, we ignore the indentation, semi-colons
    and multiple spaces between tokens by single spaces.
    """
    lines = source.split("\n")
    new_lines = []
    for line in lines:
        line = line.lstrip().replace(";", "")
        if not line:
            continue
        while "  " in line:
            line = line.replace("  ", " ")
        new_lines.append(line)
    return "\n".join(new_lines)


def test_expr1():
    expected = remove_unwanted(sm.expr_source)
    result = remove_unwanted(to_source(sm.expr_model))
    assert result == expected


def test_model1():
    expected = remove_unwanted(sm.source1)
    result = remove_unwanted(to_source(sm.model1))
    assert result == expected


def test_model2():
    expected = remove_unwanted(sm.source2)
    result = remove_unwanted(to_source(sm.model2))
    assert result == expected


def test_model3():
    expected = remove_unwanted(sm.source3)
    result = remove_unwanted(to_source(sm.model3))
    assert result == expected


def test_model4():
    expected = remove_unwanted(sm.source4)
    result = remove_unwanted(to_source(sm.model4))
    assert result == expected


def test_model5():
    expected = remove_unwanted(sm.source5)
    result = remove_unwanted(to_source(sm.model5))
    assert result == expected


def test_group():
    expected = sm.source_group
    result = to_source(sm.model_group)
    assert expected == result
