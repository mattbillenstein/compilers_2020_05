# test_typecheck.py
# uses pytest
# flake8: noqa

import os
import sys

root = os.path.join(__file__, "..", "..")
sys.path.insert(0, root)


from wabbit.typecheck import check_program
from wabbit.parse import parse_source


add_two_ints = """
2 + 3;
"""

def test_add_two_ints():
    model = parse_source(add_two_ints)
    assert check_program(model)

add_two_floats = """
2.0 + 3.0;
"""

def test_add_two_floats():
    model = parse_source(add_two_floats)
    assert check_program(model)

add_mixed_types = """
print 2 + 3.0;
print 42;
print 2 + 3 + 4 + 5.0 + 6 + 7;
"""

def test_add_mixed_types():
    model = parse_source(add_mixed_types)
    caught = False
    try:
        check_program(model)
    except TypeError as e:
        caught = True
    assert caught

print_int_expression = """
print 2 +3*4 - 5 / -6;
"""

def test_print_int_expression():
    model = parse_source(print_int_expression)
    assert check_program(model)
