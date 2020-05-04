# test_script_models.py

import script_models as sm

from wabbit.model import to_source


def remove_unwanted(source):
    lines = source.split("\n")
    new_lines = [line.lstrip() for line in lines if line]
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
    expected = remove_unwanted(sm.source2)
    result = remove_unwanted(to_source(sm.model2))
    assert result == expected
