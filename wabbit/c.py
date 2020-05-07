# c.py
# flake8: noqa
#
# In this file, we're going to transform Wabbit code to C, using it as
# a kind of low-level machine language. At first glance, this might
# sound somewhat crazy, but it actually makes sense for a number of
# reasons.  First, C compilers are standardized and ubiquitous--being
# available everywhere. Second, C is so minimal in features that you
# can use it at a low-level without having to worry about hidden
# side-effects (i.e., garbage collection, etc.).  You can also abuse
# it all sorts of horrible ways to do unnatural acts of programming
# (useful if making a new language).  Finally, in getting
# your compiler to actually "work", there may be certain runtime
# elements that are quite hard to implement or debug directly with machine
# instructions. Therefore, it might be easier to implement things in C
# as a first step.
#
# As a preliminary step, please read the short C tutorial at
#
#  https://github.com/dabeaz/compilers_2020_05/wiki/C-Programming-Tutorial
#
# Come back here when you've looked it over.  Our goal is to produce
# low-level C code where you are ONLY allowed to use the
# the following C features:
#
# 1. You can only declare uninitialized variables.  For example:
#
#         int x;
#         float y;
#         int z = 2 + 3;     // NO!!!!!!!!
#
#    All variables must be declared before use, at the top of the
#    file or function. Reminder: they are uninitialized.
#
# 2. You can only perform ONE operation at a time. Operations can
#    only involve constants and variabless.  The result of an
#    operation must always be immediately stored in a variable.  For
#    example, to compute 2 + 3 * 4, you might do this:
#
#         int _i1;      /* Temporary variables */
#         int _i2;
#
#         _i1 = 3 * 4;
#         _i2 = 2 + i1;
#
# 3. The only allowed control flow constucts are the following two
#    statements:
#
#        goto Label;
#        if (_variable) goto Label;
#
#        Label:
#           ... code ...
#
#    No, you don't get "else". And you also don't get code blocks
#    enclosed in braces { }.
#
# 4. You may print things with printf().
#
# That's it, those are the only C features you may use.  To help you
# out, Here's a small fragment of Wabbit code that executes a loop:
#
#    /* Sample Wabbit Code */
#    /* Print the first 10 factorials */
#
#    var result = 1;
#    var n = 1;
#
#    while n <= 10 {
#        result = result * n;
#        print result;
#        n = n + 1;
#    }
#
# Here's what the corresponding C code might look like (it can vary
# as long as you object the general rules above):
#
#    #include <stdio.h>
#
#    int result;
#    int n;
#
#    int main() {
#        int _i1;
#        int _i2;
#        int _i3;
#
#        result = 1;
#        n = 1;
#    L1:
#        _i1 = (n <= 10);
#        if (_i1) goto L2;
#        goto L3;
#    L2:
#        _i2 = result * n;
#        result = _i2;
#        printf("%i\n", result);
#        _i3 = n + 1;
#        n = _i3;
#        goto L1;
#    L3:
#        return 0;
#    }
#
# One thing to keep in mind... the goal is NOT to produce code for
# humans to read.  Instead, it's to produce code that is minimal and
# which can be reasoned about. There is very little actually happening
# in the above code.  It has calculations and gotos. That is basically
# it.  There is no unseen high-level magic going on. What you see
# it what it is.

# Hints:
# ------
# In the converter, you wrote code that just "did the operation"
# right there.  You used Python as the runtime environment.  In the
# type-checker, you wrote code that merely "checked the operation" to
# see if there were any errors.  In this project, you have to do a bit
# of both.  For each object in your model, you're going to write a
# function that *creates* the code for carrying out the operation.
# This will be very similar to the converter.  However, in order to
# create this code, you've got to know a few things about types. So,
# that information has to be tracked as well.  In addition, there's
# going to be a bit of extra bookkeeping related to the environment.
# For instance, in the above example, extra "C variables" such as
# "_i1", "_i2" and "_i3" are created to hold temporary values.  You'll
# need to have some way to keep track of that.
#
# Also, one other thing... everything that happens here takes place
# *after* type-checking.  Therefore, you don't need to focus on
# problem related to incorrect programs. Assume that all programs
# are fully correct with respect to their usage of types and names.

from collections import ChainMap
from functools import singledispatch
from .model import *
from .parse import parse_source

c_print = 'printf("%i\\n", {});'

c_wrap = """
#include <stdio.h>

int main() {{
   {code}
   return 0;
}}
"""


# Top-level function to handle an entire program.
def compile_program(model):
    env = ChainMap()  # is this needed?
    lines = []
    convert(model, env, lines)
    code = "\n".join(lines)
    return c_wrap.format(code=code)


@singledispatch
def convert(node, env, lines):
    raise RuntimeError(f"Can't convert {node}")

add = convert.register

# Order alphabetically so that they are easier to find

@add(Assignment)
def convert_Assignment(node, env, lines):
    value = convert(node.expression, env, lines)
    name = node.location.name
    # find the nearest environment in which this variable is known.
    for e in env.maps:
        if name in e:
            e[name] = value
            return

@add(BinOp)
def convert_BinOp(node, env, lines):
    left = convert(node.left, env, lines)
    right = convert(node.right, env, lines)
    if node.op == "+":
        return left + right
    elif node.op == "-":
        return left - right
    elif node.op == "*":
        return left * right
    elif node.op == "/":
        if isinstance(left, int):
            return left // right
        else:
            return left / right
    elif node.op == ">":
        return left > right
    elif node.op == ">=":
        return left >= right
    elif node.op == "<":
        return left < right
    elif node.op == ">=":
        return left >= right
    elif node.op == "==":
        return left == right
    elif node.op == "!=":
        return left != right
    else:
        raise RuntimeError(f"Unsupported operator {node.op}")

@add(Const)
def convert_Const(node, env, lines):
    name = node.name
    value = convert(node.value, env, lines)
    env[name] = value

@add(Compound)
def convert_Compound(node, env, lines):
    new_env = env.new_child()
    for s in node.statements:
        result = convert(s, new_env, lines)
    return result

@add(ExpressionStatement)
def convert_ExpressionStatement(node, env, lines):
    return convert(node.expression, env, lines)

@add(Float)
def convert_Float(node, env, lines):
    return node.value

@add(If)
def convert_If(node, env, lines):
    condition = convert(node.condition, env, lines)
    if condition:
        convert(node.result, env.new_child())
    elif node.alternative is not None:
        convert(node.alternative, env.new_child())

@add(Integer)
def convert_Integer(node, env, lines):
    return node.value

@add(Group)
def convert_Group(node, env, lines):
    return convert(node.expression, env, lines)

@add(Name)
def convert_Name(node, env, lines):
    return env[node.name]

@add(Print)
def convert_Print(node, env, lines):
    expr = convert(node.expression, env, lines)
    lines.append(c_print.format(expr))


@add(Statements)
def convert_Statements(node, env, lines):
    for s in node.statements:
        convert(s, env, lines)

@add(Type)
def convert_Type(node, env, lines):
    return node.type

@add(UnaryOp)
def convert_UnaryOp(node, env, lines):
    value = convert(node.value, env, lines)
    if node.op == "-":
        return -value
    else:
        return value

@add(Var)
def convert_Var(node, env, lines):
    # Assign default values of 0 if none are given
    # This is not defined in the specs.
    type = node.type
    if node.value:
        value = convert(node.value, env, lines)
    elif type == 'float':
        value = 0.0
    else:
        value = 0
    env[node.name] = value


@add(While)
def convert_While(node, env, lines):
    while True:
        condition = convert(node.condition, env, lines)
        if condition:
            convert(node.statements, env.new_child())
        else:
            break


def main(filename):
    # from .parse import parse_file
    # from .typecheck import check_program

    with open(filename) as f:
        source = f.read()

    model = parse_source(source)
    # print(model)
    # return

    # model = parse_file(filename)
    # check_program(model)
    code = compile_program(model)
    with open('out.c', 'w') as file:
        file.write(code)
    print('Wrote: out.c')


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
