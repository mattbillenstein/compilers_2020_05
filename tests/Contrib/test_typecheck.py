# test_typecheck.py
# uses pytest
# flake8: noqa

import os
import sys

root = os.path.join(__file__, "..", "..")
sys.path.insert(0, root)

import wabbit.typecheck as wab


from wabbit.typecheck import check_program
from wabbit.parse import parse_source

check_program = wab.check_program

def catch_error(model):
    # For seeing what error message might be displayed by type checker,
    # do the following in the calling function:
    #
    #   def test_something():
    #       model = parse_source(source)
    #       assert not catch_error(model)
    caught = False
    try:
        check_program(model)
    except TypeError as e:
        print(e.args[0])  # pytest only shows output when a test fails
        caught = True
        wab.clear_errors()
    return caught

# We include a few tests that should not raise any errors

add_two_ints = """
2 + 3;
"""

def test_add_two_ints():  # should not fail
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
    assert catch_error(model)


print_int_expression = """
print 2 +3*4 - 5 / -6;
"""

def test_print_int_expression():
    model = parse_source(print_int_expression)
    assert check_program(model)


# The following are type errors extracted from tests/Error/error_script.wb

def test_unary_minus_char():
    model = parse_source("print -'c';\n")
    assert catch_error(model)


def test_var_type_mismatch():
    model = parse_source("var x int = 2.5;\n")
    assert catch_error(model)


def test_const_type_mismatch():
    model = parse_source("const x float = 2;\n")
    assert catch_error(model)

bad_assignment = """
var z int;
z = 4.5;
"""

def test_bad_assignment():
    model = parse_source(bad_assignment)
    assert catch_error(model)

assign_to_constant ="""
const pi = 3.14159;
pi = 3.0;
"""

def test_assign_to_const():
    model = parse_source(assign_to_constant)
    assert catch_error(model)

if_test_bool = """
if true {

} else {

}
"""

def test_if_bool():
    model = parse_source(if_test_bool)
    assert check_program(model)


if_multiple_errors = """
var x int;
if 2 {  // not a boolean
    x = 'a';
} else {
   var y float = 2;
}
"""

def test_if_multiple_errors():
    model = parse_source(if_multiple_errors)
    assert catch_error(model)

while_condition_not_bool = """
var x = 2.5;
while x {
   x = false;
}
"""

def test_while_condition_not_bool():
    model = parse_source(while_condition_not_bool)
    assert catch_error(model)

print_int = """
print int;
"""

def test_print_int():
    model = parse_source(print_int)
    assert catch_error(model)

# The following are now caught at the parsing stage
#
# assign_to_type = """
# var int = 2;
# var float int;
# const char float = 3.14156;
# """

not_a_type = """
var x complex;
"""

def test_not_a_type():
    model = parse_source(not_a_type)
    assert catch_error(model)

while_compare_cond = """
var n = 1;

while n < 10 {
    n = n - 1;
}
print n;
"""

def test_while_cond():
    model = parse_source(while_compare_cond)
    assert check_program(model) # no error should be raised

# Finding multiple bugs while trying to check mandel_loop

mandel_part1 = """
const xmin = -2.0;
const xmax = 1.0;
const width = 80.0;
var dx float = (xmax - xmin)/width;
"""

def test_mandel_part1():
    model = parse_source(mandel_part1)
    assert check_program(model)


mandel_part2 = """
const ymax = 1.5;
var y float = ymax;
"""

def test_mandel_part2():
    model = parse_source(mandel_part2)
    assert check_program(model)

mandel_part3 = """
const xmin = -2.0;
var x float;
x = xmin;
"""

def test_mandel_part3():
    model = parse_source(mandel_part3)
    assert check_program(model)
